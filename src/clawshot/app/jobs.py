"""One isolated generation process; UI callers consume snapshots, never run the fill themselves."""

import copy
import multiprocessing
import shutil
import threading
import time
from dataclasses import dataclass
from multiprocessing.connection import wait
from pathlib import Path
from tempfile import mkdtemp

from clawshot.app.paths import absolute_path, detect_dump, output_path
from clawshot.app.schema import validate
from clawshot.pack import tree_digest

STAGES = (
    ("validate", "Check game and settings"),
    ("source", "Read your game files"),
    ("prepare", "Prepare supported checks"),
    ("generate", "Place items and check you can finish"),
    ("write", "Write and verify the mod"),
    ("publish", "Finish the new seed folder"),
)
TERMINAL = {"succeeded", "failed", "cancelled"}


@dataclass(frozen=True)
class GenerationRequest:
    dump: str
    output: str
    seed: int
    settings: str
    hookshot: str = ""

    def paths(self) -> tuple[Path, Path]:
        if type(self.seed) is not int or not -(2**53 - 1) <= self.seed <= 2**53 - 1:
            raise ValueError("Seed must be an integer within JavaScript's exact integer range")
        source = absolute_path(self.dump, "Dump", allow_links=True)
        hookshot = absolute_path(self.hookshot, "Hookshot", allow_links=True) if self.hookshot else None
        return source, output_path(self.output, source, hookshot)


def generate_seed(request: GenerationRequest, stage: Path, report) -> dict:
    """Use exactly the CLI's public preparation, seed pipeline and writer; no game launch."""
    from clawshot.pack.source import local_romfs
    from clawshot.patch import gifts, make_seed, write_seed
    from clawshot.world.load import load_spec

    report("validate")
    source, _ = request.paths()
    settings = validate(text=request.settings)
    detect_dump(str(source))
    report("source")
    with local_romfs(source, stage) as romfs:
        report("prepare")
        spec, steps = None, []
        if gifts.SHUFFLE in settings.shuffle or set(settings.shuffle).intersection(gifts.GIFT_TYPES):
            spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
            steps.append(step)
        report("generate")
        result = make_seed(romfs, request.seed, settings, spec, extra_steps=steps)
        report("write")
        written = write_seed(result, romfs, stage / "seed")
    return {
        "seed": result.seed.seed,
        "shuffled": len(result.seed.shuffled),
        "spheres": len(result.seed.spheres),
        "resources": len(written),
        "settings_string": result.seed.settings.to_string(),
    }


def _worker(run, request, stage, sender):
    try:
        result = run(request, Path(stage), lambda name: sender.send(("stage", name)))
        sender.send(("result", result))
    except BaseException as error:
        sender.send(("error", {"type": type(error).__name__, "message": str(error)}))
    finally:
        sender.close()


class Jobs:
    """At most one live worker. Worker injection is Python-only, for synthetic-world consumers/tests."""

    def __init__(self, run=generate_seed):
        self.run = run
        self.lock = threading.RLock()
        self.state = {"status": "idle", "stages": [], "result": None, "error": None}
        self.process = None
        self.thread = None
        self.started = 0.0

    def start(self, request: GenerationRequest) -> dict:
        with self.lock:
            if self.state["status"] not in TERMINAL | {"idle"} or (self.thread and self.thread.is_alive()):
                raise ValueError("A generation job is already running")
            source, out = request.paths()
            self.request = request
            self.source = source
            self.out = out
            # The suggested Documents/Clawshot parent is the only auto-created parent.
            # output_path validated its identity and all protected roots before this point.
            out.parent.mkdir(parents=True, exist_ok=True)
            self.stage = Path(mkdtemp(prefix=".clawshot-job-", dir=out.parent))
            self.started = time.monotonic()
            self.state = {
                "status": "running",
                "stages": [{"key": key, "label": label, "status": "pending", "seconds": 0} for key, label in STAGES],
                "result": None,
                "error": None,
            }
            context = multiprocessing.get_context("spawn")
            receiver, sender = context.Pipe(duplex=False)
            self.process = context.Process(target=_worker, args=(self.run, request, str(self.stage), sender))
            try:
                self.process.start()
            except BaseException:
                receiver.close()
                sender.close()
                shutil.rmtree(self.stage)
                self.state["status"] = "failed"
                raise
            sender.close()
            self.thread = threading.Thread(target=self._listen, args=(receiver,), daemon=True)
            self.thread.start()
            return self.snapshot()

    def _advance(self, name):
        now = time.monotonic()
        for row in self.state["stages"]:
            if row["status"] == "active":
                row.update(status="done", seconds=now - row.pop("started"))
            if row["key"] == name:
                row.update(status="active", started=now)
                break

    def _publish(self, result):
        # Reserve an absent destination with exclusive mkdir: POSIX rename may replace an empty directory.
        # Only this freshly reserved directory is cleaned on failure. Cancellation and publication serialize.
        _, out = self.request.paths()
        seed = self.stage / "seed"
        digest = tree_digest(seed)
        out.mkdir()
        try:
            seed.rename(out / "seed")
        except BaseException:
            shutil.rmtree(out)
            raise
        self.state.update(
            status="succeeded",
            result=result | {"output": str(out), "output_sha256": digest, "dump": str(self.source)},
        )
        self._finish_stage("done")

    def _finish_stage(self, status):
        for row in self.state["stages"]:
            if row["status"] == "active":
                row.update(status=status, seconds=time.monotonic() - row.pop("started"))

    def _listen(self, receiver):
        received = None
        try:
            while True:
                # An early-killed Windows spawn can retain a duplicated pipe handle.
                # Watch the process sentinel too; EOF alone can block cancellation.
                if receiver not in wait((receiver, self.process.sentinel)):
                    break
                kind, value = receiver.recv()
                with self.lock:
                    if self.state["status"] == "cancelling":
                        continue
                    if kind == "stage":
                        self._advance(value)
                    elif kind == "error":
                        self.state.update(status="failed", error=value)
                        break
                    elif kind == "result":
                        received = value
                        break
        except EOFError:
            pass
        finally:
            receiver.close()
            self.process.join()
            with self.lock:
                try:
                    if self.state["status"] == "cancelling":
                        self.state["status"] = "cancelled"
                        self._finish_stage("cancelled")
                    elif received is not None and self.process.exitcode == 0:
                        self._advance("publish")
                        self._publish(received)
                    elif self.state["status"] != "failed":
                        self.state.update(
                            status="failed",
                            error={
                                "type": "WorkerExit",
                                "message": f"Generation worker exited {self.process.exitcode}",
                            },
                        )
                    if self.state["status"] == "failed":
                        self._finish_stage("failed")
                except Exception as error:
                    self.state.update(status="failed", error={"type": type(error).__name__, "message": str(error)})
                    self._finish_stage("failed")
                finally:
                    shutil.rmtree(self.stage)

    def snapshot(self) -> dict:
        with self.lock:
            state = copy.deepcopy(self.state)
            for row in state["stages"]:
                if "started" in row:
                    row["seconds"] = time.monotonic() - row.pop("started")
            state["seconds"] = time.monotonic() - self.started if self.started else 0
            return state

    def cancel(self) -> dict:
        with self.lock:
            if self.state["status"] == "running":
                self.state["status"] = "cancelling"
                self.process.terminate()
            return self.snapshot()

    def close(self):
        self.cancel()
        if self.thread is not None:
            self.thread.join()
