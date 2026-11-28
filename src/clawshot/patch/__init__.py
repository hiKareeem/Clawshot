"""From a seed to a mod folder: the item-to-actor table, the patch plan and the writer.

    out = make_seed(romfs, 12345, Settings())     # census, remake pool, fill, beatability search, plan
    write_seed(out, romfs, Path("seed-12345"))     # romfs overlay, spoiler.json and play-note.md

The chest pool uses ``remake_vanilla``; opt-in Shop locations use the native shop
catalog; opt-in Token checks keep their native token pool and are written by
``clawshot.patch.tokens`` (new pickup packs, spoiler ``patch.tokens``). The fill and
beatability search are ``clawshot.generate``'s.
"""

import json
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from clawshot.census import definitions as census_definitions
from clawshot.census.scan import scan
from clawshot.generate import Seed, Settings, from_placements, generate, key_families, play_note, prepare, spoiler
from clawshot.generate import hints as stone_hints
from clawshot.generate import names as location_names
from clawshot.generate import tokens as token_policy
from clawshot.generate.fill import SWORD_PEDESTAL_SOURCE, shuffled_locations
from clawshot.patch import (
    bags,
    bombs,
    custom_items,
    darunia,
    drops,
    freestanding,
    gamedata,
    gifts,
    scrubs,
    shops,
    text,
    tokens,
    trials,
)
from clawshot.patch import events as chest_events
from clawshot.patch import items as item_actors
from clawshot.patch import receive_event as receive_event_patch
from clawshot.patch.custom_items import Foreign
from clawshot.patch.plan import Links, PatchError, Plan, link, make_plan, remake_vanilla, restrict_event_openings
from clawshot.patch.write import FileChanges, NewFile, WrittenFile, write
from clawshot.settings import CATALOG, validate_logic_overrides
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
    item_names: dict[str, str] = field(default_factory=dict)
    """The game's (English) names of the items the hints name, as the stones say them."""
    new_files: dict[str, NewFile] = field(default_factory=dict)
    """Files the dump does not hold: custom item/Skulltula actor packs and receive-event flow."""
    token_sources: tuple[tokens.SourceChange, ...] = ()
    """Every shuffled Token location's source and grant, for the spoiler's ``patch.tokens``."""
    steps: tuple[str, ...] = ()
    """The optional cosmetic steps that ran (:data:`OPTIONAL_STEPS`, in that order), for the spoiler's
    ``patch.steps``: a bug report shows which build a seed has without working it out from the settings."""

    def spoiler(self) -> dict[str, Any]:
        patch = self.plan.as_dict()
        if self.token_sources:
            patch["tokens"] = [source.as_dict() for source in self.token_sources]
        patch["steps"] = list(self.steps)
        return spoiler(self.seed, self.item_names) | {"patch": patch}

    def spoiler_json(self) -> str:
        return json.dumps(self.spoiler(), indent=2, ensure_ascii=False) + "\n"


OCARINA_GET_MODEL = "ocarina_get_model"
SONG_GET_EFFECTS = "song_get_effects"
OCARINA_PICKUPS = "ocarina_pickups"
OPTIONAL_STEPS = (OCARINA_GET_MODEL, SONG_GET_EFFECTS, OCARINA_PICKUPS)
"""The optional cosmetic get-display steps ``make_seed`` runs when the settings could produce what they show."""


def make_seed(
    romfs: str | Path,
    seed: int,
    settings: Settings,
    spec: Mapping[str, Any] | None = None,
    *,
    extra_steps: Sequence[PatchStep] = (),
    placements: Mapping[str, str] | None = None,
    foreign: Mapping[str, Foreign] | None = None,
    possessive_text: bool = False,
    receive_event: bool = False,
    event_models: Collection[str] | None = None,
) -> SeedOutput:
    """Fill a seed; kind-specific steps turn placements into decompressed file transforms.

    With ``placements`` the shuffled locations take those items instead of Clawshot's fill (another placer's, such
    as an Archipelago multiworld's; see ``generate.from_placements``), and no Gossip Stone hints are chosen.
    ``foreign`` names the player and item of each location placed ``Archipelago Item``; ``possessive_text`` makes
    the get line of every item the seed holds say "your" (``clawshot.patch.custom_items``); ``receive_event`` adds
    the event a runtime module requests to give an item with the game's own notice (``patch.receive_event``).
    A solo seed places neither custom item and sets neither switch, so none of this changes its output."""
    spec = load_spec() if spec is None else spec
    validate_logic_overrides(spec, settings.logic)
    definitions = census_definitions.load()
    if scrubs.SHUFFLE in settings.shuffle:
        spec, settings, step = scrubs.seed_setup(spec, settings)
        extra_steps = (*extra_steps, step)
    if freestanding.SHUFFLE in settings.shuffle:
        spec = freestanding.restrict_spec(spec, definitions)
    fast_settings = gamedata.load()
    if settings.dungeon_rewards:
        from clawshot.patch import rewards

        extra_steps = (*extra_steps, lambda placements: rewards.changes(romfs, placements))
    names = [*settings.fast_start, *CATALOG["forest"][settings.forest]["fast_start"]]
    from clawshot.patch import start_items

    chosen = [
        *gamedata.load_always(),
        *gamedata.select(fast_settings, names),
        *start_items.initial_values(settings),
        *trials.initial_values(seed, settings.trials_count),
    ]
    _, world = prepare(spec, settings, seed=seed)
    table = item_actors.load()
    table.check(world.items)
    shuffled = shuffled_locations(world, settings)
    chests = [name for name in shuffled if world.locations[name].type == "Chest"]
    shop_locations = tuple(name for name in shuffled if world.locations[name].type == "Shop")
    floor_pickups = sum(world.locations[name].type in (drops.SHUFFLE, freestanding.SHUFFLE) for name in shuffled)
    key_pickups = sum(
        world.locations[name].type in (key_families.FLOOR_KEY_SOURCE, key_families.HIDEOUT_KEY_SOURCE)
        for name in shuffled
    )
    token_locations = [name for name in shuffled if world.locations[name].type == token_policy.SHUFFLE]
    sword_pickups = sum(world.locations[name].type == SWORD_PEDESTAL_SOURCE for name in shuffled)
    if (
        len(chests) + len(shop_locations) + floor_pickups + len(token_locations) + key_pickups + sword_pickups
        != len(shuffled)
        and not extra_steps
    ):
        raise PatchError("non-chest shuffle needs a kind-specific extra patch step")
    token_rewards = token_policy.REWARDS if token_locations else {}
    if unadmitted := sorted({family for _, family in token_rewards.values()} - token_policy.ADMITTED_FAMILIES):
        raise PatchError(f"Token rewards name grant families production does not admit: {unadmitted}")
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
    token_sources = tokens.link_sources(token_locations, definitions, census) if token_locations else {}
    vanilla = remake_vanilla(world, links, table)
    spec = restrict_event_openings(spec, world, links, chest_events.load())
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
    custom = custom_step(romfs, out, links, table, foreign or {}, possessive_text=possessive_text)
    changes = tuple(step(out.placements) for step in extra_steps)
    flags = list(custom.flags)
    new_files = dict(custom.new_files)
    token_rows: tuple[tokens.SourceChange, ...] = ()
    from clawshot.patch import ocarina_pickup, songs

    # Built here, composed at their usual place below: a Skulltula pickup may take one of their actors as its donor.
    # Both run when the settings could produce what they show (PR #41's rule, the maintainers' option 2); a placement
    # the rule does not cover is refused rather than shown wrongly (S8).
    shuffled_placements = {name: out.placements[name] for name in out.shuffled}
    song_pickups = songs.pickups_possible(settings.shuffle, settings.songs)
    song_delivery = songs.build(romfs, pickups=song_pickups) if songs.songs_can_move(settings.shuffle) else None
    if song_delivery is None and (moved := songs.moved_songs(out.placements, out.world, table)):
        raise PatchError(f"{moved} hold a moved song, but the settings do not run the song get effects")
    if not song_pickups and (placed := songs.placed_pickups(shuffled_placements, out.world, table)):
        raise PatchError(f"{placed} hold a song as a world pickup, but the settings do not build the song pickups")
    ocarina_delivery = None
    if ocarinas := ocarina_pickup.pickups_for(settings.shuffle):
        # The ocarinas' glow reuses the songs' light clone in static: added here only when no song step adds it.
        ocarina_delivery = ocarina_pickup.build(romfs, ocarinas, with_static=song_delivery is None)
    elif ocarinas := ocarina_pickup.needed(shuffled_placements, out.world, table):
        raise PatchError(f"{ocarinas} sit at world pickups, but the settings do not run the ocarina pickups")
    if token_sources:
        placed_actors = {
            token_rewards[out.placements[name]][0] for name in token_sources if out.placements[name] in token_rewards
        }
        generated = {}
        if any(actor.startswith(tokens.GENERATED_PREFIX) for actor in placed_actors):
            steps = [(d.changes, d.new_files) for d in (song_delivery, ocarina_delivery) if d is not None]
            generated = tokens.generated_donors(romfs, steps)
        # Token insertion validates the original dump row snapshot; custom rows then insert by name.
        delivery, token_rows = tokens.seed_delivery(
            romfs, out.placements, token_sources, links.names, census, rewards=token_rewards, generated=generated
        )
        changes += (delivery.changes,)
        if overlap := sorted(new_files.keys() & delivery.new_files.keys()):
            raise PatchError(f"custom items and Skulltula pickups both create {overlap}")
        new_files.update(delivery.new_files)
    if custom.changes:
        changes += (custom.changes,)
    from clawshot.patch import floor_keys, jail_keys

    floor_placements = {
        name: out.placements[name]
        for name in out.shuffled
        if out.world.locations[name].type == key_families.FLOOR_KEY_SOURCE
    }
    jail_placements = {
        name: out.placements[name]
        for name in out.shuffled
        if out.world.locations[name].type == key_families.HIDEOUT_KEY_SOURCE
    }
    if jail_placements:
        changes += (jail_keys.build(romfs, jail_placements).changes,)
    if floor_placements:
        delivery = floor_keys.build(romfs, floor_placements)
        changes += (delivery.changes,)
        if overlap := sorted(new_files.keys() & delivery.new_files.keys()):
            raise PatchError(f"custom items and floor-key pickups both create {overlap}")
        new_files.update(delivery.new_files)
    if receive_event:
        event_changes, event_files = receive_event_patch.changes(romfs)
        changes += (event_changes,)
        new_files.update(event_files)
        flags.append(receive_event_patch.FLAG)
    if flags:
        from clawshot.patch.gifts import game_data_transform

        changes += ({gamedata.GAME_DATA_LIST: game_data_transform(flags)},)
    # Fast-start initial values compose before gift flag additions; its flow edits run before other flow steps.
    if scrubs.SHUFFLE not in settings.shuffle:
        changes += (scrubs.changes({}),)
    # Pin the native win boundary before kind-specific gift/bag guards rewrite the reward event.
    changes = (gamedata.changes(chosen), gifts.skull_kid_changes(), *changes)
    if world.settings.get("free_time_travel", False):
        from clawshot.patch.age import changes as age_changes

        changes += (age_changes(out.placements, free_time_travel=True),)
    from clawshot.patch import (
        dampe_first_race,
        dampe_safety,
        door,
        equipment,
        master_sword,
        mido_schedule,
        reward_bridge,
        scene_gifts,
        talon,
    )

    changes += (
        door.changes(out.placements, mode=settings.door_of_time, dungeon_rewards=settings.dungeon_rewards),
        start_items.changes(settings),
        bombs.changes(enabled=world.settings.get("bombs_without_bracelet", False)),
        equipment.changes(),
        *([master_sword.changes(out.placements)] if settings.shuffle_master_sword else []),
        dampe_safety.changes(),
        dampe_first_race.changes(),
        text.dampe_refusal_changes(romfs),
        talon.changes(romfs, out.placements),
        scene_gifts.changes(out.placements, table),
    )
    changes += (reward_bridge.changes(mode=settings.bridge, count=settings.bridge_count),)
    scrub_previews = {name: out.placements[name] for name in out.shuffled if name in scrubs.SALES}
    changes += (text.scrub_hint_changes(romfs, scrub_previews, table, scrubs.sale_prices(settings)),)
    changes += (text.static_hint_changes(romfs, out, table),)
    # Prize lines name a moved gift's item (event-items 1.4), whatever event_item_models says (1.5).
    from clawshot.patch import event_lines

    moved_lines = event_lines.moved_lines(
        event_lines.load(),
        shuffled_placements,
        {name: out.world.locations[name].vanilla for name in out.shuffled},
        table.actor,
    )
    changes += (event_lines.changes(romfs, moved_lines),)
    if settings.event_item_models or event_models is not None:
        # Events show the given item through containers (event-items, setting event_item_models); the pilot's
        # event_models keyword limits it to the events named.
        from clawshot.patch import event_models as models_step
        from clawshot.patch import event_props as props_data

        prop_checks = {prop.check for prop in props_data.load().props}
        moved_props = {
            name: table.actor(item)
            for name, item in shuffled_placements.items()
            if name in prop_checks and item != out.world.locations[name].vanilla
        }
        model_changes, model_files = models_step.seed_changes(romfs, moved_props, events=event_models)
        changes += (model_changes,)
        if overlap := sorted(new_files.keys() & model_files.keys()):
            raise PatchError(f"event containers and another step both create {overlap}")
        new_files.update(model_files)
    # Every seed (event-items Q2/D9): the bridge Saria has an actor of her own, so her farewell shows one ocarina.
    from clawshot.patch import saria_farewell

    farewell_changes, farewell_files = saria_farewell.changes(romfs)
    changes += (farewell_changes,)
    if overlap := sorted(new_files.keys() & farewell_files.keys()):
        raise PatchError(f"Saria's farewell actor and another step both create {overlap}")
    new_files.update(farewell_files)
    item_names: dict[str, str] = {}
    if out.hints:
        item_names, hint_changes = hint_step(romfs, out, table)
        changes += (hint_changes,)
    catalog = location_names.load()
    hookshot_locations = [
        catalog[name].name if name in catalog else name
        for name, item in sorted(out.placements.items())
        if item in ("Hookshot", "Progressive Hookshot")
    ]
    changes += (text.sheik_hint_changes(romfs, hookshot_locations),)
    changes += (trials.changes(romfs, seed=seed, count=settings.trials_count),)
    fast_files = (
        *door.build(romfs, mode=settings.door_of_time, dungeon_rewards=settings.dungeon_rewards),
        *reward_bridge.build(romfs, mode=settings.bridge, count=settings.bridge_count),
    )
    kept_mido = settings.forest != "open"
    changes += (mido_schedule.changes(kept=kept_mido),)
    fast_files += tuple(mido_schedule.build(romfs, kept=kept_mido))
    plan = make_plan(out, links, table, chest_events.load(), overrides=custom.actors)
    from clawshot.patch import getitem, keys, ocarina, progressive, progressive_bonus, scene_handoff

    handoff = scene_handoff.build(romfs, skip_saria_farewell=settings.skip_saria_farewell, prior_changes=changes)
    changes += (handoff.changes,)
    new_files.update(handoff.new_files)
    # Darunia's source flag and forward-only Fire step precede Event127's bonus wrapper, which keeps its next.
    changes += (darunia.changes(),)
    # Bonus guards and source-bound selections precede bag guards; unrelated native callers stay unchanged.
    changes += (progressive_bonus.changes(romfs, out, prior_changes=changes),)
    plan, key_changes = keys.changes(romfs, plan, prior_changes=changes)
    changes += (key_changes,)
    plan, progressive_changes = progressive.changes(romfs, plan, prior_changes=changes)
    changes += (progressive_changes, bags.changes(romfs))
    # Both normal and camera-obstructed world receipts precede the shared keep-Time guard.
    if ocarina_delivery is not None:
        changes += (ocarina_pickup.receipt_changes(romfs),)
    changes += (ocarina.changes(romfs, prior_changes=changes),)
    # Cosmetic get-display steps follow settings, not actual placements (PR #41 option 2).
    # Gift-only settings also need the ocarina model: display hand-overs crash with native packs (r22 arms07–09).
    steps: list[str] = []
    ocarinas = getitem.ocarina_locations(out.placements, out.shuffled, table)
    gift_ocarinas = [name for name in ocarinas if out.world.locations[name].type in gifts.GIFT_TYPES]
    if gift_ocarinas:
        receipts = gifts.check_steps(gifts.scan_gifts(romfs), definitions)
        missing = [name for name in gift_ocarinas if not receipts.get(name)]
        if missing:
            raise PatchError(f"ocarina gifts lack an audited receipt; native-pack hand-overs are unsafe: {missing}")
    # Last on the ocarina packs and after prior ActorInfo row edits. Missing model inputs fail closed.
    if getitem.ocarina_get_model_possible(settings.shuffle):
        changes += (getitem.ocarina_changes(romfs),)
        steps.append(OCARINA_GET_MODEL)
    elif ocarinas:
        raise PatchError(f"{ocarinas} hold an ocarina, but the settings do not run the ocarina get model")
    # Song get effects: when the settings let songs leave their places. Songs show an ocarina with their own effect;
    # their floor pickups, for the floor and Skulltula kinds, only when the settings could place a song there
    # (songs.pickups_possible; Kareem's rule, rounds/r21-pr41.md finding 4). Last on ActorInfo and the song packs.
    if song_delivery is not None:
        delivery = song_delivery
        changes += (delivery.changes,)
        if overlap := sorted(new_files.keys() & delivery.new_files.keys()):
            raise PatchError(f"another step and the song pickups both create {overlap}")
        new_files.update(delivery.new_files)
        steps.append(SONG_GET_EFFECTS)
    # The ocarinas' world actors, glow and pickup receipt: when the settings could put an ocarina on a floor or at a
    # Skulltula (ocarina_pickup.pickups_for). Rows inserted by name.
    if ocarina_delivery is not None:
        delivery = ocarina_delivery
        changes += (delivery.changes,)
        if overlap := sorted(new_files.keys() & delivery.new_files.keys()):
            raise PatchError(f"another step and the ocarina pickups both create {overlap}")
        new_files.update(delivery.new_files)
        steps.append(OCARINA_PICKUPS)
    return SeedOutput(out, links, plan, changes, fast_files, item_names, new_files, token_rows, tuple(steps))


def custom_step(
    romfs: str | Path,
    seed: Seed,
    links: Links,
    table: item_actors.ItemActors,
    foreign: Mapping[str, Foreign],
    *,
    possessive_text: bool,
) -> custom_items.CustomItems:
    """The custom items the seed places (Nothing, other players' items) and the "your" get lines."""
    by_item: dict[str, list[str]] = {item: [] for item in custom_items.CUSTOM_ITEMS}
    for name in seed.shuffled:
        if seed.placements.get(name) in by_item:
            by_item[seed.placements[name]].append(name)
    placed = [name for names in by_item.values() for name in names]
    not_chests = sorted(name for name in placed if name not in links.chests)
    if not_chests:
        raise PatchError(f"Nothing and other players' items go only to chests so far, not {not_chests[:5]}")
    unnamed = sorted(set(by_item[custom_items.FOREIGN_ITEM]) - set(foreign))
    if unnamed:
        raise PatchError(f"no player and item named for the Archipelago items at {unnamed[:5]}")
    stray = sorted(set(foreign) - set(by_item[custom_items.FOREIGN_ITEM]))
    if stray:
        raise PatchError(f"other players' items named for locations that do not hold one: {stray[:5]}")
    own = []
    if possessive_text:
        from clawshot.progressive import CHAINS

        for name in seed.shuffled:
            item = seed.placements[name]
            if item in table.actors:
                own.append(table.actors[item])
            if item in CHAINS:
                own.extend(tier.actor for tier in CHAINS[item])
    return custom_items.changes(
        romfs, nothing_locations=by_item[custom_items.NOTHING_ITEM], foreign=foreign, own_actors=own
    )


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
        output.plan,
        romfs,
        out,
        extra_changes=output.extra_changes,
        fast_start_files=output.fast_start_files,
        new_files=output.new_files,
    )
    (out / "spoiler.json").write_text(spoiler_text, encoding="utf-8", newline="\n")
    (out / "play-note.md").write_text(note_text, encoding="utf-8", newline="\n")
    return written
