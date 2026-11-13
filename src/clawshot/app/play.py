"""Verified per-seed Play; planning is read-only and the pack owns native launch rules."""

import threading

from clawshot.app.library import verified_seed
from clawshot.app.paths import absolute_path
from clawshot.pack.runtime import RUNNING_GAME, launch_plan, play_refusal, start_game


def play_plan(result: dict | None, game: str) -> dict:
    seed = verified_seed(result)
    if not isinstance(game, str) or not game.strip():
        raise ValueError("Choose and check your Hookshot or Longshot folder on Game, then press Play.")
    try:
        installation = absolute_path(game, "Game folder", allow_links=True)
    except (OSError, ValueError) as error:
        raise ValueError("Choose and check your Hookshot or Longshot folder on Game, then press Play again.") from error
    return launch_plan(seed.parent, installation)


class Player:
    def __init__(self):
        self.lock = threading.RLock()
        self.process = None
        self.paths = {}

    def start(self, result: dict | None, game: str) -> dict:
        if refusal := play_refusal():
            raise ValueError(refusal)
        with self.lock:
            if self.process is not None and self.process.poll() is None:
                raise ValueError(RUNNING_GAME)
            plan = play_plan(result, game)
            try:
                self.process, options = start_game(plan)
            except OSError as error:
                raise ValueError(
                    f"{plan['game']} could not start. Check its folder on Game and try Play again: {error}"
                ) from error
            self.paths = {key: plan[key] for key in ("game", "user", "log")} | {
                "output": result["output"],
                "options": options,
            }
            return {"started": True, **self.snapshot()}

    def snapshot(self) -> dict:
        with self.lock:
            return {"running": self.process is not None and self.process.poll() is None, **self.paths}
