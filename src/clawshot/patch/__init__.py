"""From a seed to a mod folder: the item-to-actor table, the patch plan and the writer.

    out = make_seed(romfs, 12345, Settings())     # census, remake pool, fill, beatability search, plan
    write_seed(out, romfs, Path("seed-12345"))     # romfs overlay, spoiler.json and play-note.md

The chest pool uses ``remake_vanilla``; opt-in Shop locations use the native shop
catalog. The fill and beatability search are ``clawshot.generate``'s.
"""

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from functools import partial
from pathlib import Path
from typing import Any

from clawshot.census import definitions as census_definitions
from clawshot.census.scan import scan
from clawshot.generate import Seed, Settings, from_placements, generate, play_note, prepare, spoiler
from clawshot.generate import hints as stone_hints
from clawshot.generate import names as location_names
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import drops, freestanding, gamedata, scrubs, shops, text
from clawshot.patch import events as chest_events
from clawshot.patch import items as item_actors
from clawshot.patch.plan import Links, PatchError, Plan, link, make_plan, remake_vanilla
from clawshot.patch.write import FileChanges, WrittenFile, write
from clawshot.settings import CATALOG
from clawshot.world.load import load_spec

__all__ = ["PatchError", "PatchStep", "SeedOutput", "check_dungeon_items", "make_seed", "write_seed"]

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
    item_names: dict[str, str] = field(default_factory=dict)
    """The game's (English) names of the items the hints name, as the stones say them."""

    def spoiler(self) -> dict[str, Any]:
        return spoiler(self.seed, self.item_names) | {"patch": self.plan.as_dict()}

    def spoiler_json(self) -> str:
        return json.dumps(self.spoiler(), indent=2, ensure_ascii=False) + "\n"


def check_dungeon_items(settings: Settings) -> None:
    """Keep unverified dungeon attribution out of game output, not the synthetic fill."""
    if settings.dungeon_items == "anywhere":
        raise PatchError(
            "dungeon_items='anywhere' is not enabled for seed output: generic key/map/compass actors "
            "do not encode target dungeons, and named-dungeon grants have not passed in-game testing. "
            "Use dungeon_items='own_dungeon'."
        )


def make_seed(
    romfs: str | Path,
    seed: int,
    settings: Settings,
    spec: Mapping[str, Any] | None = None,
    *,
    extra_steps: Sequence[PatchStep] = (),
    placements: Mapping[str, str] | None = None,
    game_data_flags: Sequence[str] = (),
) -> SeedOutput:
    """Fill a seed; kind-specific steps turn placements into decompressed file transforms.

    With ``placements`` the shuffled locations take those items instead of Clawshot's fill (an Archipelago slot,
    ``clawshot.ap``; see ``generate.from_placements``) and no Gossip Stone hints are chosen. ``game_data_flags``
    names saved Bools to add to the GameDataList (``gifts.add_flags``), for a runtime module's own state."""
    check_dungeon_items(settings)
    if "Token" in settings.shuffle:
        raise PatchError(
            "Token shuffle is not enabled: per-enemy grant selection and GoldTokenGmdHash persistence "
            "are unverified. The r7-drops native-token-boomerang experiment changes all tokens, not a seed."
        )
    spec = load_spec() if spec is None else spec
    definitions = census_definitions.load()
    if scrubs.SHUFFLE in settings.shuffle:
        spec, settings, step = scrubs.seed_setup(spec, settings)
        extra_steps = (*extra_steps, step)
    if freestanding.SHUFFLE in settings.shuffle:
        spec = freestanding.restrict_spec(spec, definitions)
    fast_settings = gamedata.load()
    names = [*settings.fast_start, *CATALOG["forest"][settings.forest]["fast_start"]]
    chosen = gamedata.select(fast_settings, names)
    _, world = prepare(spec, settings)
    table = item_actors.load()
    table.check(world.items)
    chests = [name for name in shuffled_locations(world, settings) if world.locations[name].type == "Chest"]
    shop_locations = tuple(name for name in shuffled_locations(world, settings) if world.locations[name].type == "Shop")
    floor_pickups = sum(
        world.locations[name].type in (drops.SHUFFLE, freestanding.SHUFFLE)
        for name in shuffled_locations(world, settings)
    )
    if (
        len(chests) + len(shop_locations) + floor_pickups != len(shuffled_locations(world, settings))
        and not extra_steps
    ):
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
    census = scan(romfs)
    links = link(world, chests, definitions, census)
    vanilla = remake_vanilla(world, links, table)
    if freestanding.SHUFFLE in settings.shuffle:
        settings, step = freestanding.seed_setup(world, settings, census, definitions, vanilla)
        extra_steps = (*extra_steps, step)
    if drops.SHUFFLE in settings.shuffle:
        settings, step = drops.seed_setup(world, settings, census, definitions, vanilla)
        extra_steps = (*extra_steps, step)
    if placements is None:
        out = generate(spec, seed, settings, vanilla=vanilla)
    else:
        out = from_placements(spec, seed, settings, placements, vanilla=vanilla)
    changes = tuple(step(out.placements) for step in extra_steps)
    if game_data_flags:
        from clawshot.patch.gifts import game_data_transform

        changes += ({gamedata.GAME_DATA_LIST: game_data_transform(list(game_data_flags))},)
    if any(setting.game_data for setting in chosen):
        changes = ({gamedata.GAME_DATA_LIST: partial(gamedata.patch_initial_values, chosen=chosen)}, *changes)
    if world.settings.get("free_time_travel", False):
        from clawshot.patch.age import changes as age_changes

        changes += (age_changes(out.placements, free_time_travel=True),)
    from clawshot.patch import door

    changes += (door.changes(out.placements, mode=settings.door_of_time),)
    item_names: dict[str, str] = {}
    if out.hints:
        item_names, hint_changes = hint_step(romfs, out, table)
        changes += (hint_changes,)
    catalog = location_names.load()
    hookshot_locations = [
        catalog[name].name if name in catalog else name
        for name, item in sorted(out.placements.items())
        if item == "Hookshot"
    ]
    changes += (text.sheik_hint_changes(romfs, hookshot_locations),)
    # GameData defaults compose before gift flag additions; only cutscene component files are prebuilt.
    event_settings = {s.name: replace(s, game_data={}) for s in chosen if s.skippable}
    fast_files = tuple(gamedata.build(romfs, list(event_settings), event_settings)) if event_settings else ()
    fast_files += tuple(door.build(romfs, mode=settings.door_of_time))
    plan = make_plan(out, links, table, chest_events.load())
    return SeedOutput(out, links, plan, changes, fast_files, item_names)


def hint_step(romfs: str | Path, seed: Seed, table: item_actors.ItemActors) -> tuple[dict[str, str], FileChanges]:
    """The seed's hints as text changes: every language archive's stone lines (English: D26) and, with
    ``hints = "always"``, the flow that lets stones speak without the Mask of Truth. Returns the item names used."""
    names = text.item_names(romfs, [hint.item for hint in seed.hints if hint.item], table)
    catalog = location_names.load()
    lines = {
        hint.label: stone_hints.text(
            hint,
            lambda item: names.get(item, item),
            lambda name: catalog[name].name if name in catalog else name,
            marked=True,
        )
        for hint in seed.hints
    }
    changes = text.hint_changes(romfs, lines, text.languages(romfs), without_mask=seed.settings.hints == "always")
    return names, changes


def write_seed(output: SeedOutput, romfs: str | Path, out: str | Path) -> list[WrittenFile]:
    """Write changed romfs files, ``spoiler.json`` and the readable ``play-note.md``."""
    out = Path(out)
    log = output.spoiler()
    spoiler_text = json.dumps(log, indent=2, ensure_ascii=False) + "\n"
    note_text = play_note(output.seed, log)
    written = write(
        output.plan, romfs, out, extra_changes=output.extra_changes, fast_start_files=output.fast_start_files
    )
    (out / "spoiler.json").write_text(spoiler_text, encoding="utf-8", newline="\n")
    (out / "play-note.md").write_text(note_text, encoding="utf-8", newline="\n")
    return written
