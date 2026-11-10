"""Verified per-seed Play; planning is read-only and the pack owns native launch rules."""

import sys
import threading

from clawshot.app.paths import absolute_path, detect_dump
from clawshot.pack import tree_digest
from clawshot.pack.runtime import RUNNING_GAME, launch_plan, start_game


def play_plan(result: dict | None, hookshot: str) -> dict:
    if result is None:
        raise ValueError("Generate a seed first, then press Play.")
    if not isinstance(hookshot, str) or not hookshot.strip():
        raise ValueError("Choose and check your Hookshot folder on Game, then press Play.")
    try:
        root = absolute_path(result["output"], "Seed output")
        digest = tree_digest(root / "seed")
    except (OSError, ValueError) as error:
        raise ValueError(
            "The seed files are missing, linked or unreadable. Generate a new seed, then press Play."
        ) from error
    if not (root / "seed/romfs").is_dir():
        raise ValueError("The seed folder is missing. Generate a new seed, then press Play.")
    if digest != result["output_sha256"]:
        raise ValueError("This seed's files have changed. Generate a new seed before pressing Play.")
    try:
        detect_dump(result["dump"])
    except (OSError, ValueError) as error:
        raise ValueError(
            "Check your game files again on Game, then generate a new seed before pressing Play."
        ) from error
    try:
        installation = absolute_path(hookshot, "Hookshot", allow_links=True)
    except (OSError, ValueError) as error:
        raise ValueError("Choose and check your Hookshot folder on Game, then press Play again.") from error
    return launch_plan(root, installation)


class Player:
    def __init__(self):
        self.lock = threading.RLock()
        self.process = None
        self.paths = {}

    def start(self, result: dict | None, hookshot: str) -> dict:
        if sys.platform != "win32":
            raise ValueError("Play needs Windows. Open the seed folder and load romfs as a mod in your emulator.")
        with self.lock:
            if self.process is not None and self.process.poll() is None:
                raise ValueError(RUNNING_GAME)
            plan = play_plan(result, hookshot)
            try:
                self.process = start_game(plan)
            except OSError as error:
                raise ValueError(
                    f"Hookshot could not start. Check its folder on Game and try Play again: {error}"
                ) from error
            self.paths = {key: plan[key] for key in ("user", "log")} | {"output": result["output"]}
            return {"started": True, **self.snapshot()}

    def snapshot(self) -> dict:
        with self.lock:
            return {"running": self.process is not None and self.process.poll() is None, **self.paths}
