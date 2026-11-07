"""From a seed to a mod folder: the item-to-actor table, the patch plan and the writer.

    out = make_seed(romfs, 12345, Settings())     # census, remake pool, fill, beatability search, plan
    write_seed(out, romfs, Path("seed-12345"))     # <dir>/romfs/... and <dir>/spoiler.json

The pool is what the remake's chests hold (``remake_vanilla``), as logic items; the fill and the beatability
search are ``clawshot.generate``'s.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clawshot.census import definitions as census_definitions
from clawshot.census.scan import scan
from clawshot.generate import Seed, Settings, generate, spoiler
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import events as chest_events
from clawshot.patch import items as item_actors
from clawshot.patch.plan import Links, PatchError, Plan, link, make_plan, remake_vanilla
from clawshot.patch.write import WrittenFile, write
from clawshot.world.load import build_world, load_spec

__all__ = ["PatchError", "SeedOutput", "make_seed", "write_seed"]


@dataclass(frozen=True)
class SeedOutput:
    seed: Seed
    links: Links
    plan: Plan

    def spoiler(self) -> dict[str, Any]:
        return spoiler(self.seed) | {"patch": self.plan.as_dict()}

    def spoiler_json(self) -> str:
        return json.dumps(self.spoiler(), indent=2, ensure_ascii=False) + "\n"


def make_seed(romfs: str | Path, seed: int, settings: Settings, spec: Mapping[str, Any] | None = None) -> SeedOutput:
    """Run the census on ``romfs`` (read only), fill a seed from the remake's chest contents and plan its patch."""
    spec = load_spec() if spec is None else spec
    world = build_world(spec, settings.logic)
    table = item_actors.load()
    table.check(world.items)
    links = link(world, shuffled_locations(world, settings), census_definitions.load(), scan(romfs))
    out = generate(spec, seed, settings, vanilla=remake_vanilla(world, links, table))
    return SeedOutput(out, links, make_plan(out, links, table, chest_events.load()))


def write_seed(output: SeedOutput, romfs: str | Path, out: str | Path) -> list[WrittenFile]:
    """Write the seed's changed files under ``<out>/romfs`` and its spoiler log as ``<out>/spoiler.json``."""
    out = Path(out)
    written = write(output.plan, romfs, out)
    (out / "spoiler.json").write_text(output.spoiler_json(), encoding="utf-8", newline="\n")
    return written
