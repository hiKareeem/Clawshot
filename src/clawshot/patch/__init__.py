"""From a seed to a mod folder: the item-to-actor table, the patch plan and the writer.

    out = make_seed(romfs, 12345, Settings())     # census, remake pool, fill, beatability search, plan
    write_seed(out, romfs, Path("seed-12345"))     # <dir>/romfs/... and <dir>/spoiler.json

The pool is what the remake's chests hold (``remake_vanilla``), as logic items; the fill and the beatability
search are ``clawshot.generate``'s.
"""

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clawshot.census import definitions as census_definitions
from clawshot.census.scan import scan
from clawshot.generate import Seed, Settings, generate, prepare, spoiler
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import events as chest_events
from clawshot.patch import items as item_actors
from clawshot.patch.plan import Links, PatchError, Plan, link, make_plan, remake_vanilla
from clawshot.patch.write import FileChanges, WrittenFile, write
from clawshot.world.load import load_spec

__all__ = ["PatchError", "PatchStep", "SeedOutput", "make_seed", "write_seed"]

# A kind-specific step closes over its census/romfs context. File transforms receive decompressed bytes;
# multiple steps touching one file compose in registration order, after the chest changes.
PatchStep = Callable[[Mapping[str, str]], FileChanges]


@dataclass(frozen=True)
class SeedOutput:
    seed: Seed
    links: Links
    plan: Plan
    extra_changes: tuple[FileChanges, ...] = ()

    def spoiler(self) -> dict[str, Any]:
        return spoiler(self.seed) | {"patch": self.plan.as_dict()}

    def spoiler_json(self) -> str:
        return json.dumps(self.spoiler(), indent=2, ensure_ascii=False) + "\n"


def make_seed(
    romfs: str | Path,
    seed: int,
    settings: Settings,
    spec: Mapping[str, Any] | None = None,
    *,
    extra_steps: Sequence[PatchStep] = (),
) -> SeedOutput:
    """Fill a seed; kind-specific steps turn placements into decompressed file transforms."""
    spec = load_spec() if spec is None else spec
    _, world = prepare(spec, settings)
    table = item_actors.load()
    table.check(world.items)
    chests = [name for name in shuffled_locations(world, settings) if world.locations[name].type == "Chest"]
    if len(chests) != len(shuffled_locations(world, settings)) and not extra_steps:
        raise PatchError("non-chest shuffle needs a kind-specific extra patch step")
    links = link(world, chests, census_definitions.load(), scan(romfs))
    out = generate(spec, seed, settings, vanilla=remake_vanilla(world, links, table))
    changes = tuple(step(out.placements) for step in extra_steps)
    return SeedOutput(out, links, make_plan(out, links, table, chest_events.load()), changes)


def write_seed(output: SeedOutput, romfs: str | Path, out: str | Path) -> list[WrittenFile]:
    """Write the seed's changed files under ``<out>/romfs`` and its spoiler log as ``<out>/spoiler.json``."""
    out = Path(out)
    written = write(output.plan, romfs, out, extra_changes=output.extra_changes)
    (out / "spoiler.json").write_text(output.spoiler_json(), encoding="utf-8", newline="\n")
    return written
