"""Seeds: the fill, the beatability search on every seed, and the spoiler log.

    seed = generate(load_spec(), 12345, Settings())
    text = spoiler_json(seed)

Same seed, settings, world data and generator version give the same placements and the same spoiler bytes: the
only randomness is ``random.Random(seed)``, and every list the fill walks is in world-file order.
"""

import json
import random
from collections.abc import Mapping
from dataclasses import asdict, dataclass, replace
from importlib.metadata import version
from typing import Any

from clawshot.generate import hints as stone_hints
from clawshot.generate import names as location_names
from clawshot.generate.fill import (
    FillError,
    Settings,
    check_beatable,
    fill,
    return_guarantee_conflict,
    shuffled_locations,
)
from clawshot.generate.itembar import age_locked_pickups
from clawshot.generate.progressive import normalize_pool, prepare_spec, restrict_settings
from clawshot.generate.route import NoChildOpening, opening
from clawshot.world.load import build_world
from clawshot.world.model import World
from clawshot.world.shops import with_shop_prices, with_shop_slots

__all__ = ["FillError", "Seed", "Settings", "generate", "play_note", "prepare", "spoiler", "spoiler_json", "world_spec"]

FILL_ATTEMPTS = 10


@dataclass(frozen=True)
class Seed:
    world: World
    seed: int
    settings: Settings
    placements: dict[str, str]
    """Every placed location (shuffled or vanilla) to its item, in world order."""
    shuffled: list[str]
    """The locations whose items were shuffled, in world order."""
    spheres: list[list[str]]
    """The beatability search's spheres: location names collected in each."""
    hints: tuple[stone_hints.Hint, ...] = ()
    """One hint per Gossip Stone (``clawshot.generate.hints``), in world order; none for a world without stones."""


def world_spec(spec: Mapping[str, Any], settings: Settings) -> Mapping[str, Any]:
    """The spec cut down to ``settings.areas`` (the regions in those census areas and the area-less start regions,
    whose exits elsewhere then dangle) with ``settings.goal``; the spec unchanged when no areas are given."""
    if not settings.areas:
        return spec
    areas = set(settings.areas)
    regions = [r for r in spec["regions"] if r.get("area") is None or r.get("area") in areas]
    if not any(r.get("area") in areas for r in regions):
        raise FillError(f"no region of the world lies in the areas {sorted(areas)}")
    kept = {name for r in regions for name in r.get("locations", {})}
    locations = {name: info for name, info in spec.get("locations", {}).items() if name in kept}
    return {**spec, "regions": regions, "locations": locations, "goal": settings.goal or spec["goal"]}


def prepare(spec: Mapping[str, Any], settings: Settings) -> tuple[Settings, World]:
    """The settings as a seed uses them, and the world they build.

    With ``dungeon_items = "anywhere"`` the logic setting ``keysanity`` is set too, where the world has it.
    ``open_forest`` and the legacy ``skip_mido`` rule flag derive from the same forest mode the overlay patches.
    Native setup also uses this compilation before its pool overrides are known. The UI checks return-kit
    construction against the spec; :func:`generate` checks it against the effective native pool before filling.
    """
    spec = prepare_spec(spec)
    logic = dict(settings.logic)
    if "open_forest" in spec.get("settings", {}):
        if "open_forest" in logic and logic["open_forest"] != settings.forest:
            raise FillError("open_forest logic must agree with the seed's forest setting")
        logic["open_forest"] = settings.forest
    if "skip_mido" in spec.get("settings", {}):
        skipped = settings.forest == "open"
        if "skip_mido" in logic and logic["skip_mido"] != skipped:
            raise FillError("skip_mido logic must agree with the seed's forest setting")
        logic["skip_mido"] = skipped
    if "door_of_time" in spec.get("settings", {}):
        if "door_of_time" in logic and logic["door_of_time"] != settings.door_of_time:
            raise FillError("door_of_time logic must agree with the seed's door_of_time setting")
        logic["door_of_time"] = settings.door_of_time
        for source, target in (
            ("age_return_door_inventory", "age_return_fill_inventory"),
            ("age_return_door_families", "age_return_fill_families"),
        ):
            modes = spec["settings"].get(source, {})
            if source in spec["settings"]:
                logic[target] = modes.get(settings.door_of_time, spec["settings"][target])
    if settings.dungeon_items == "anywhere" and "keysanity" in spec.get("settings", {}):
        if logic.get("keysanity") is False:
            raise FillError("dungeon_items = 'anywhere' needs the logic setting keysanity = true")
        logic["keysanity"] = True
    settings = replace(settings, logic=logic)
    if "Shop" in settings.shuffle:
        spec = with_shop_slots(spec, settings.shop_slots)
    spec = with_shop_prices(spec, settings.shuffle, settings.shop_prices, settings.cheap_deku_shield)
    if "Shop" in settings.shuffle:
        held = {name: ("Shop",) for name in spec.get("items", {}) if name.startswith("Buy ")}
        settings = replace(settings, item_location_types={**settings.item_location_types, **held})
    world = build_world(world_spec(spec, settings), settings.logic)
    return restrict_settings(world, settings), world


def generate(
    spec: Mapping[str, Any],
    seed: int,
    settings: Settings,
    attempts: int = FILL_ATTEMPTS,
    vanilla: Mapping[str, str] | None = None,
) -> Seed:
    """Build the world for ``settings`` (:func:`prepare`), fill it from ``random.Random(seed)`` and check it can be
    beaten.

    ``vanilla`` gives the remake's own item for locations where it differs from the world's (OoT Randomizer's):
    the pool is then what the remake hands out (``clawshot.patch.remake_vanilla``).

    A failed fill is retried with the same generator (so a retry is as deterministic as the first try), up to
    ``attempts`` times; then :class:`FillError` is raised.
    """
    settings, world = prepare(spec, settings)
    vanilla = dict(vanilla or {})
    vanilla.update(normalize_pool(world, settings, vanilla))
    unknown = sorted(name for name in vanilla if name not in world.locations)
    if unknown:
        raise FillError(f"vanilla items given for locations the world does not have: {unknown}")
    bad = sorted(item for item in vanilla.values() if item not in world.items)
    if bad:
        raise FillError(f"vanilla items the world does not know: {bad}")
    if conflict := return_guarantee_conflict(world, settings, vanilla):
        raise FillError(conflict)
    rng = random.Random(seed)
    errors: list[str] = []
    for _ in range(attempts):
        try:
            placements = fill(world, settings, rng, vanilla)
            break
        except FillError as e:
            errors.append(str(e))
    else:
        raise FillError(f"no beatable fill in {attempts} attempts; last: {errors[-1]}")
    spheres = check_beatable(world, placements)
    out = Seed(world, seed, settings, placements, shuffled_locations(world, settings), spheres)
    return replace(out, hints=stone_hints.choose(out, settings.hints, settings.hint_distribution))


def _required_items(seed: Seed, sources: tuple[str, ...], visits: Mapping[str, dict]) -> list[dict[str, Any]]:
    by_item: dict[str, list[str]] = {}
    for source in sources:
        item = visits[source]["item"] if source in visits else seed.placements[source]
        by_item.setdefault(item, []).append(source)
    return [{"item": item, "count": len(names), "sources": names} for item, names in by_item.items()]


PROGRESSIVE_REPLAY_NOTE = (
    "A progressive copy gives the next native tier of its family when it is opened, so its concrete item depends on"
    " collection order. The canonical replay walks this seed's full search spheres in order, fixed native rewards"
    " included, and names the tier each copy gives there. It is one deterministic order: not a play order, not"
    " gameplay proof and not a promise for another route. Before the return gate opens the search keeps child Link's"
    " inventory as an independent prefix, and a player who opens the same chests in another order receives other"
    " tiers."
)


def _progressive_grants(seed: Seed) -> dict[str, dict[str, Any]]:
    """Each location holding a progressive family (``clawshot.progressive.CHAINS``), in world order: the family, its
    native tiers in order, its canonical sphere, the tier the canonical sphere replay gives there and whether that tier
    was already owned (a harmless leftover); those three are null where the search never collects the location.

    The replay walks ``seed.spheres`` in order, each sphere in its world order, with no randomness. Start items and
    fixed rewards (shuffled or native bonuses) record their tier's canonical pouch identity, never a copy; a fixed
    native magic source (``clawshot.progressive.MAGIC_SOURCES``: a spell, the Lens, magic arrows) records its own
    identity, which models its native one-meter floor and is not a Magic Meter ownership claim. Each progressive copy
    takes :func:`clawshot.progressive.next_tier` of what is owned at that point and records the identity of the tier
    it gives; a copy whose tier is already owned (the chain is complete, for example after a native bonus) is a
    leftover."""
    from clawshot.progressive import CHAINS, MAGIC_SOURCES, next_tier

    families = {name: item for name, item in seed.placements.items() if item in CHAINS}
    if not families:
        return {}
    fixed = {tier.item: tier.owned for tiers in CHAINS.values() for tier in tiers} | MAGIC_SOURCES
    owned = {fixed[item] for item in seed.world.start_items if item in fixed}
    given: dict[str, tuple[int, str, bool]] = {}
    for index, sphere in enumerate(seed.spheres, 1):
        for name in sphere:
            item = seed.placements[name]
            if item in CHAINS:
                tier = next_tier(item, owned)
                given[name] = (index, tier.item, tier.owned in owned)
                owned.add(tier.owned)
            elif item in fixed:
                owned.add(fixed[item])
    return {
        name: {
            "family": family,
            "possible_tiers": [tier.item for tier in CHAINS[family]],
            "canonical_sphere": given[name][0] if name in given else None,
            "given_in_canonical_sphere_replay": given[name][1] if name in given else None,
            "leftover_in_canonical_replay": given[name][2] if name in given else None,
        }
        for name, family in families.items()
    }


def spoiler(seed: Seed, item_names: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Keep world-keyed placements/spheres and add physical descriptions, a replayed opening witness and the hints.

    ``opening_route`` is a child-only route or null; ``opening_route_unavailable`` explains a configured opening that
    child Link alone cannot complete in this seed (adult Link first), else null.

    Items keep their logic names everywhere; ``item_names`` in the log adds, for each placed item whose name differs,
    the name the player sees: the remake's (``clawshot.generate.names.item_names``), or the game's where the
    ``item_names`` argument (logic item -> the game's name) gives it. Hints word items with those same names, as the
    stones say them.

    A progressive family keeps its own label ("Progressive Hookshot") in every placement, hint and name, never its
    base tier's. ``progressive_grants`` adds, per location holding one, the family's tiers in order and the tier the
    canonical sphere replay gives (:func:`_progressive_grants`), under :data:`PROGRESSIVE_REPLAY_NOTE`; ``item_names``
    then also covers those tiers."""
    items = seed.world.items
    spheres = [
        {name: seed.placements[name] for name in sphere if items[seed.placements[name]].progression}
        for sphere in seed.spheres
    ]
    catalog = location_names.load()
    shops = location_names.shops(seed)
    scrub_prices = seed.world.settings.get("scrub_sale_prices", {})

    def describe(name: str) -> dict[str, Any]:
        description = catalog.get(name)
        # A custom world has no physical census: retain its own name/region, without inventing IDs or prices.
        result = (
            asdict(description)
            if description is not None
            else {"name": name, "where": seed.world.locations[name].region, "oot_randomizer_name": ""}
        )
        if name in shops:
            result.update(shops[name])
        elif name in scrub_prices:
            result.update(price=scrub_prices[name], opens="Native scrub puzzle and once-sale gate")
        return result

    locations = {name: describe(name) for name in seed.shuffled}
    route = opening(seed)
    opening_log = None
    opening_unavailable = None
    if isinstance(route, NoChildOpening):
        opening_unavailable = {"name": route.name, "event": route.event, "region": route.region, "reason": route.reason}
    elif route is not None:
        goal_regions = list(dict.fromkeys(event.region for event in seed.world.events if event.name == route.event))

        def describe_step(step):
            if step.kind == "visit":
                info = route.visits[step.location]
            elif step.kind == "collect":
                info = describe(step.location) | {"item": seed.placements[step.location]}
            else:
                info = {
                    "name": route.name if step.kind == "enter" else route.event,
                    "where": route.region if step.kind == "enter" else " / ".join(goal_regions),
                    "item": None,
                }
            return info | {
                "kind": step.kind,
                "location": step.location,
                "requires": _required_items(seed, step.requires, route.visits),
                "alternatives": [describe_step(alternative) for alternative in step.alternatives],
            }

        opening_log = {
            "name": route.name,
            "event": route.event,
            "region": route.region,
            "steps": [describe_step(step) for step in route.steps],
        }
    progressive = _progressive_grants(seed)
    display = {**location_names.item_names(), **(item_names or {})}
    display.update((entry["family"], entry["family"]) for entry in progressive.values())
    named = {tier for entry in progressive.values() for tier in entry["possible_tiers"]}
    named.update(seed.placements.values())

    def item_name(item: str) -> str:
        return display.get(item, item)

    def location_name(name: str) -> str:
        return catalog[name].name if name in catalog else name

    hint_log = [
        {
            "stone": hint.stone,
            "where": stone_hints.stone_place(hint.stone),
            "label": hint.label,
            "kind": hint.kind,
            "text": stone_hints.text(hint, item_name, location_name),
            "area": stone_hints.area_name(hint.area) if hint.area else None,
            "location": hint.location,
            "item": hint.item,
        }
        for hint in seed.hints
    ]
    return {
        "generator": f"clawshot {version('clawshot')}",
        "seed": seed.seed,
        "settings": seed.settings.as_dict(),
        "settings_string": seed.settings.to_string(),
        "placements": {name: seed.placements[name] for name in seed.shuffled},
        "item_names": {item: display[item] for item in sorted(display.keys() & named) if display[item] != item},
        "locations": locations,
        "progressive_grants": {"note": PROGRESSIVE_REPLAY_NOTE, "locations": progressive},
        "opening_route": opening_log,
        "opening_route_unavailable": opening_unavailable,
        "age_locked_pickups": [asdict(pickup) for pickup in age_locked_pickups(seed)],
        "spheres": [sphere for sphere in spheres if sphere],
        "hints": hint_log,
    }


def spoiler_json(seed: Seed, item_names: Mapping[str, str] | None = None) -> str:
    return json.dumps(spoiler(seed, item_names), indent=2, ensure_ascii=False) + "\n"


def _markdown_cell(text: str) -> str:
    return text.replace("\n", " ").replace("|", r"\|")


def play_note(seed: Seed, log: Mapping[str, Any] | None = None) -> str:
    """Render the logic-derived opening and every shuffled destination from one spoiler snapshot, naming items as the
    player sees them (the log's ``item_names``), and each progressive copy's tiers with the tier the canonical sphere
    replay gives (the log's ``progressive_grants``)."""
    log = spoiler(seed) if log is None else log
    descriptions = log["locations"]
    names = log["item_names"]

    def shown(item: str) -> str:
        return names.get(item, item)

    collected = {name: index for index, sphere in enumerate(seed.spheres, 1) for name in sphere}
    lines = [f"# Clawshot seed {seed.seed}", ""]
    lines.extend(
        [
            "## Age-locked items",
            "",
            "New games initialize an empty Deku Nut slot (0/20). Child Bow first followed by working Boomerang use"
            " without a reload passed Kareem's 2026-11-12 check.",
            "Existing saves are unchanged. In saves started with older builds, Save and Continue before using"
            " other items after an age-unusable pickup; changing areas does not clear that older item-bar jam.",
            "",
        ]
    )
    if log.get("age_locked_pickups"):
        lines.extend(
            [
                "These shuffled rewards are reachable by the wrong age at their first search frontier.",
                "Both ages in a row means a tie, not that the item is usable by both.",
                "This is an age-usability reference, not a required play order.",
                "",
                "| Item | Usable age | First reachable as | Location | World / OoTR check | Where |",
                "|---|---|---|---|---|---|",
            ]
        )
        for pickup in log["age_locked_pickups"]:
            description = descriptions[pickup["location"]]
            cells = (
                shown(pickup["item"]),
                pickup["usable_age"],
                " / ".join(pickup["first_ages"]),
                description["name"],
                pickup["location"],
                description["where"],
            )
            lines.append("| " + " | ".join(_markdown_cell(cell) for cell in cells) + " |")
    else:
        lines.append("No shuffled age-locked reward is reachable by the wrong age at its first search frontier.")
    lines.append("")
    lines.extend(
        [
            "## Trade-slot order",
            "",
            "Trading items stay at their native checks. Wake child Talon with the Cucco and show Zelda's Letter"
            " before taking Anju's adult Pocket Egg.",
            "Child and adult trade items share one displayed slot; an owned adult trade item hides the Cucco."
            " Save and Continue does not change that ownership-based slot choice.",
            "",
        ]
    )
    progressive = log.get("progressive_grants") or {}
    lines.extend(
        [
            "## Progressive items",
            "",
            "Hookshot, strength, scale, wallet, bomb bag, quiver, slingshot bag and magic upgrades are always"
            " progressive (Kareem, 2026-11-13); no setting turns them back into fixed items.",
            "Only chests hold progressive copies. Every other check kind (gifts, shops, scrubs, floor pickups) cannot"
            " choose a tier, so it never carries one.",
            "Where a native check still gives a fixed upgrade (Darunia's Bracelet, a Great Fairy's magic, a Skulltula"
            " wallet, a minigame bag or scale), the chests also hold a full set of copies, one per tier, in place of"
            " ordinary filler. Logic counts only copies toward upgrade tiers; native rewards are bonuses and never"
            " downgrade what you own.",
            "Child-strength exception: logic requires Darunia's native Bracelet route (his door, Zelda's Lullaby and"
            " Saria's Song), without adding a copy tier. An early copy Bracelet can physically work out of logic,"
            " but logic never relies on it. Adult strength remains copy-only.",
            "The model rising from a progressive chest is always the family's first tier (the Hookshot, the Goron"
            " Bracelet, ...). The get window and the item you receive are the next tier above the highest one you"
            " own.",
            "A copy opened when its family has no tier left for you (for example after such a native bonus) is a"
            " harmless leftover: it gives the last tier again, and no tier becomes unobtainable.",
            "Progressive Strength gives child Link's Goron Bracelet first while it is missing, even to adult Link;"
            " the gauntlets follow. Progressive Quiver and Progressive Slingshot give their weapon first, then the"
            " bigger bags. Progressive Magic gives the double meter once you have any magic, including the meter a"
            " spell, the Lens or magic arrows open.",
            "",
        ]
    )
    if progressive.get("locations"):
        lines.extend(
            [
                progressive["note"],
                "",
                "| Sphere | Location | World / OoTR check | Family | Tiers in order | Given in canonical replay |",
                "|---|---|---|---|---|---|",
            ]
        )
        grants = sorted(
            progressive["locations"].items(),
            key=lambda entry: entry[1]["canonical_sphere"] or len(seed.spheres) + 1,
        )
        for name, grant in grants:
            given = grant["given_in_canonical_sphere_replay"]
            if not given:
                reward = "— (the search does not collect it)"
            elif grant.get("leftover_in_canonical_replay"):
                reward = f"{shown(given)} again (harmless leftover)"
            else:
                reward = shown(given)
            cells = (
                str(grant["canonical_sphere"] or "—"),
                descriptions[name]["name"] if name in descriptions else name,
                name,
                shown(grant["family"]),
                " → ".join(shown(tier) for tier in grant["possible_tiers"]),
                reward,
            )
            lines.append("| " + " | ".join(_markdown_cell(cell) for cell in cells) + " |")
    else:
        lines.append("This seed places no progressive copy.")
    lines.append("")
    unavailable = log["opening_route_unavailable"]
    if unavailable is not None:
        lines.extend(
            [
                f"## Opening: {unavailable['name']}",
                "",
                unavailable["reason"],
                "The seed passed the beatability search; the spheres below are its full search, not a play order.",
                "",
            ]
        )
    route = log["opening_route"]
    if route is not None:
        lines.extend(
            [
                f"## Opening: {route['name']}",
                "",
                "This is one replayed logic witness, not every optional sphere find.",
                "Entry preparation covers the planned clear, not just reaching the lobby.",
                "Prices are before conditional discounts; logic checks wallet capacity, not cash earned.",
                "An alternative row replaces its visit; it is not an additional required purchase.",
                "",
                "| Step | Action | Check / where / world identity | Item | Needed beforehand | Price / shelf release |",
                "|---|---|---|---|---|---|",
            ]
        )
        indices = {
            step["location"]: i for i, step in enumerate(route["steps"], 1) if step["kind"] in ("collect", "visit")
        }

        def render_step(index: str, step: Mapping[str, Any], alternative: bool = False) -> None:
            action = (
                ("Buy" if "price" in step else "Collect") if step["kind"] == "collect" else step["kind"].capitalize()
            )
            if alternative:
                action += " (alternative)"
            place = f"{step['name']} — {step['where']}"
            if step["location"] not in (step["name"], step["where"]):
                place += f" [{step['location']}]"
            needed = []
            for requirement in step["requires"]:
                item = shown(requirement["item"])
                if requirement["count"] != 1:
                    item += f" × {requirement['count']}"
                references = ", ".join(str(indices[source]) for source in requirement["sources"])
                needed.append(f"{item} (step {references})")
            sale = f"{step['price']} rupees; {step['opens']}" if "price" in step else "—"
            if "not_equipped" in step:
                sale += f"; no {shown(step['not_equipped'])} equipped (unequip it if owned)"
            reward = shown(step["item"]) if step["item"] else "—"
            cells = (index, action, place, reward, "; ".join(needed) or "None", sale)
            lines.append("| " + " | ".join(_markdown_cell(cell) for cell in cells) + " |")

        for index, step in enumerate(route["steps"], 1):
            render_step(str(index), step)
            for alternative in step["alternatives"]:
                render_step(f"{index} alt", alternative, alternative=True)
        lines.append("")
    lines.extend(
        [
            "## All shuffled rewards",
            "",
            "Full search spheres include non-progression finds; this table is not a mandatory play order.",
            "— means the search did not collect that check. Settings are in `spoiler.json`.",
            "",
            "| Sphere | Location | Where | World / OoTR check | Item |",
            "|---|---|---|---|---|",
        ]
    )
    for name in sorted(seed.shuffled, key=lambda name: collected.get(name, len(seed.spheres) + 1)):
        description = descriptions[name]
        cells = (
            str(collected.get(name, "—")),
            description["name"],
            description["where"],
            name,
            shown(seed.placements[name]),
        )
        lines.append("| " + " | ".join(_markdown_cell(cell) for cell in cells) + " |")
    if log.get("hints"):
        mode = log["settings"].get("hints", "always")
        lines.extend(
            [
                "",
                "## Gossip Stones",
                "",
                "Every stone speaks without the Mask of Truth."
                if mode == "always"
                else "Stones speak only to child Link wearing the Mask of Truth.",
                "Which stone of a pair or row carries which label is not settled where its place says so.",
                "",
                "| Stone | Where | Says | Kind | Points at |",
                "|---|---|---|---|---|",
            ]
        )
        for hint in log["hints"]:
            item = shown(hint["item"]) if hint["item"] else None
            target = " — ".join(part for part in (hint["location"], item) if part) or "—"
            cells = (hint["stone"], hint["where"], hint["text"], hint["kind"], target)
            lines.append("| " + " | ".join(_markdown_cell(cell) for cell in cells) + " |")
    return "\n".join(lines) + "\n"
