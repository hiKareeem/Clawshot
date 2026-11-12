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
from clawshot.generate.fill import FillError, Settings, check_beatable, fill, shuffled_locations
from clawshot.generate.itembar import age_locked_pickups
from clawshot.generate.prepare import prepare, world_spec
from clawshot.generate.route import opening
from clawshot.world.model import World

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
    unknown = sorted(name for name in vanilla if name not in world.locations)
    if unknown:
        raise FillError(f"vanilla items given for locations the world does not have: {unknown}")
    bad = sorted(item for item in vanilla.values() if item not in world.items)
    if bad:
        raise FillError(f"vanilla items the world does not know: {bad}")
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


def spoiler(seed: Seed, item_names: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Keep world-keyed placements/spheres and add physical descriptions, a replayed opening witness and the hints.

    Items keep their logic names everywhere; ``item_names`` in the log adds, for each placed item whose name differs,
    the name the player sees: the remake's (``clawshot.generate.names.item_names``), or the game's where the
    ``item_names`` argument (logic item -> the game's name) gives it. Hints word items with those same names, as the
    stones say them."""
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
    if route is not None:
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
    display = {**location_names.item_names(), **(item_names or {})}

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
        "item_names": {
            item: display[item]
            for item in sorted(display.keys() & set(seed.placements.values()))
            if display[item] != item
        },
        "locations": locations,
        "opening_route": opening_log,
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
    player sees them (the log's ``item_names``)."""
    log = spoiler(seed) if log is None else log
    descriptions = log["locations"]
    names = log["item_names"]

    def shown(item: str) -> str:
        return names.get(item, item)

    collected = {name: index for index, sphere in enumerate(seed.spheres, 1) for name in sphere}
    lines = [f"# Clawshot seed {seed.seed}", ""]
    lines.extend(
        [
            "## Age-locked items: Save and Continue",
            "",
            "After obtaining an item Link's current age cannot use, Save and Continue before using other items.",
            "Picking up the Fairy Bow as child has jammed the ZR item bar; changing areas did not fix it, but Save and"
            " Continue did.",
            "Other age-locked items below are precautions, not individually confirmed failures.",
            "",
        ]
    )
    if log.get("age_locked_pickups"):
        lines.extend(
            [
                "These shuffled rewards are reachable by the wrong age at their first search frontier.",
                "Both ages in a row means a tie, not that the item is usable by both.",
                "This is not a required play order; reload only if you take the item at an unusable age.",
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
    lines.extend(["", "Optional later wrong-age pickups still need the same Save and Continue precaution.", ""])
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
