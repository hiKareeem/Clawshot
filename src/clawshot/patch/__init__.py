"""From a seed to a mod folder: the item-to-actor table, the patch plan and the writer.

    out = make_seed(romfs, 12345, Settings())     # census, remake pool, fill, beatability search, plan
    write_seed(out, romfs, Path("seed-12345"))     # <dir>/romfs/... and <dir>/spoiler.json

The chest pool uses ``remake_vanilla``; opt-in Shop locations use the native shop
catalog. The fill and beatability search are ``clawshot.generate``'s.
"""

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from functools import partial
from pathlib import Path
from typing import Any

from clawshot.census import definitions as census_definitions
from clawshot.census.scan import scan
from clawshot.generate import Seed, Settings, generate, prepare, spoiler
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import events as chest_events
from clawshot.patch import gamedata, scrubs, shops
from clawshot.patch import items as item_actors
from clawshot.patch.plan import Links, PatchError, Plan, link, make_plan, remake_vanilla
from clawshot.patch.write import FileChanges, WrittenFile, write
from clawshot.settings import CATALOG
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
    fast_start_files: tuple[gamedata.BuiltFile, ...] = ()

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
    if "Token" in settings.shuffle:
        raise PatchError(
            "Token shuffle is not enabled: replacement pickups have not proved the GoldTokenGmdHash "
            "collection callback or persistence. Run the r6-tokens ranch control/rupee/shield experiments first."
        )
    spec = load_spec() if spec is None else spec
    if scrubs.SHUFFLE in settings.shuffle:
        spec, settings, step = scrubs.seed_setup(spec, settings)
        extra_steps = (*extra_steps, step)
    fast_settings = gamedata.load()
    names = [*settings.fast_start, *CATALOG["forest"][settings.forest]["fast_start"]]
    chosen = gamedata.select(fast_settings, names)
    _, world = prepare(spec, settings)
    table = item_actors.load()
    table.check(world.items)
    chests = [name for name in shuffled_locations(world, settings) if world.locations[name].type == "Chest"]
    shop_locations = tuple(name for name in shuffled_locations(world, settings) if world.locations[name].type == "Shop")
    if len(chests) + len(shop_locations) != len(shuffled_locations(world, settings)) and not extra_steps:
        raise PatchError("non-chest shuffle needs a kind-specific extra patch step")
    if shop_locations or settings.cheap_deku_shield:
        extra_steps = (
            *extra_steps,
            shops.patch_step(
                romfs,
                shop_locations,
                shop_prices=settings.shop_prices,
                cheap_deku_shield=settings.cheap_deku_shield,
            ),
        )
    links = link(world, chests, census_definitions.load(), scan(romfs))
    out = generate(spec, seed, settings, vanilla=remake_vanilla(world, links, table))
    changes = tuple(step(out.placements) for step in extra_steps)
    if any(setting.game_data for setting in chosen):
        changes = ({gamedata.GAME_DATA_LIST: partial(gamedata.patch_initial_values, chosen=chosen)}, *changes)
    if world.settings.get("free_time_travel", False):
        from clawshot.patch.age import changes as age_changes

        changes += (age_changes(out.placements, free_time_travel=True),)
    # GameData defaults compose before gift flag additions; only cutscene component files are prebuilt.
    event_settings = {s.name: replace(s, game_data={}) for s in chosen if s.skippable}
    fast_files = tuple(gamedata.build(romfs, list(event_settings), event_settings)) if event_settings else ()
    return SeedOutput(out, links, make_plan(out, links, table, chest_events.load()), changes, fast_files)


def write_seed(output: SeedOutput, romfs: str | Path, out: str | Path) -> list[WrittenFile]:
    """Write the seed's changed files under ``<out>/romfs`` and its spoiler log as ``<out>/spoiler.json``."""
    out = Path(out)
    written = write(
        output.plan, romfs, out, extra_changes=output.extra_changes, fast_start_files=output.fast_start_files
    )
    (out / "spoiler.json").write_text(output.spoiler_json(), encoding="utf-8", newline="\n")
    return written
