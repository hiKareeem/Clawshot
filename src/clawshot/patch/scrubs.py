"""Saved one-time scrub rewards; repeat/rotating vendors remain vanilla.

Keep the Banc offer selectors: the common flow dispatches known names, not arbitrary
items. Rewrite every grant of a logical check, including both capacity tiers, and
its explicit selection identity. Prices, puzzle, cancel/shortfall paths, and the
success-only saved completion flags stay native. See r6-tokens.md for all 21 actors.
"""

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any

from clawshot.formats import evfl
from clawshot.generate import Settings, prepare
from clawshot.patch import items as item_actors
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

FLOW = "Enemy_Scrub_Business_Common"
PATH = f"Event/EventFlow/{FLOW}.bfevfl.zs"
SHUFFLE = "Scrub"
CAPACITIES = ("Deku Stick Capacity", "Deku Nut Capacity")


@dataclass(frozen=True)
class Sale:
    ids: tuple[int, ...]
    flag: str
    price: int
    grants: tuple[tuple[str, str], ...]
    selection: str | None = None


SALES = {
    "HF Deku Scrub Grotto": Sale(
        (1888007325063123154, 10364468093017215295),
        "HyruleField_Enemy_Scrub_Business_HeartPiece_01",
        100,
        (("Event645", "Obj_Heart_Piece"),),
        "Event653",
    ),
    "DMC Deku Scrub": Sale(
        (2518138296199711695,),
        "DeathMountain_Enemy_Scrub_Business_HeartPiece_01",
        100,
        (("Event293", "Obj_Heart_Piece"),),
        "Event144",
    ),
    "LW Deku Scrub Near Bridge": Sale(
        (182031956235860994, 7488448334396031424, 5406759280757349546, 11192313919554167152),
        "LostWood_Enemy_Scrub_Business_DekuStickPouch_01",
        40,
        (
            ("Event317", "Item_StickBag_Large"),
            ("Event322", "Item_StickBag_Medium"),
            ("Event555", "Item_StickBag_Medium"),
        ),
    ),
    "LW Deku Scrub Grotto Front": Sale(
        (4328741615941752705, 5764461665617243979),
        "Lostwood_Enemy_Scrub_Business_DekuNutsPouch_01",
        40,
        (("Event318", "Item_NutBag_Large"), ("Event326", "Item_NutBag_Medium")),
    ),
}


def patch_flowchart(fc: evfl.Flowchart, placements: Mapping[str, str]) -> None:
    """Validate every target before mutation; preserve all control flow and flags."""
    if fc.name != FLOW or set(placements) - SALES.keys():
        raise PatchError(f"{FLOW}: invalid flow or unsupported scrub checks {sorted(placements)}")
    edits = []
    for check, item in placements.items():
        if not isinstance(item, str) or not item:
            raise PatchError(f"{check}: empty or invalid reward")
        sale = SALES[check]
        for name, old in sale.grants:
            found = [e for e in fc.events if e.name == name]
            if len(found) != 1:
                raise PatchError(f"{FLOW}/{name}: expected one grant, found {len(found)}")
            event = found[0]
            if not (
                isinstance(event, evfl.SubFlowEvent)
                and event.flowchart in ("", FLOW)
                and event.entry_point == "SimpleShopSub_Scrub_Business_OneTime"
                and (event.params or {}).get("ActorName") == old
                and event.params.get("Price") == sale.price
            ):
                raise PatchError(f"{FLOW}/{name}: stale sale {event!r}")
            edits.append((event.params, "ActorName", item))
        if sale.selection:
            found = [e for e in fc.events if e.name == sale.selection]
            if len(found) != 1:
                raise PatchError(f"{FLOW}/{sale.selection}: expected one selection event")
            event = found[0]
            if not (
                isinstance(event, evfl.ActionEvent)
                and fc.actors[event.actor].name == "GameDataActor"
                and fc.actors[event.actor].actions[event.action] == "EventTriggerSetGameDataString64"
                and (event.params or {}).get("GameDataName") == "Shop_SelectItemName"
                and event.params.get("Value") == "Obj_Heart_Piece"
            ):
                raise PatchError(f"{FLOW}/{sale.selection}: stale selection {event!r}")
            edits.append((event.params, "Value", item))
    for params, key, value in edits:
        params[key] = value


def changes(placements: Mapping[str, str]) -> FileChanges:
    """Actor-name placements for supported checks, for the common writer."""
    if unknown := set(placements) - SALES.keys():
        raise PatchError(f"unsupported scrub checks: {sorted(unknown)}")
    if not placements:
        return {}
    placements = dict(placements)

    def transform(data: bytes) -> bytes:
        tree = evfl.read(data)
        if tree.flowchart is None:
            raise PatchError(f"{PATH}: no flowchart")
        patch_flowchart(tree.flowchart, placements)
        out = evfl.write(tree)
        if evfl.read(out) != tree:
            raise PatchError(f"{PATH}: changed flow does not read back")
        return out

    return {PATH: transform}


def seed_setup(spec: Mapping[str, Any], settings: Settings):
    """Four reviewed once-sale families; one pool reward per shared saved flag.

    Public Scrub covers the two translated scrub types without exposing an internal
    alias in the settings string. Capacities use fixed Medium actors (D16), held to
    these destinations until their grants have been tested in chests.
    """
    locations = {}
    for name, info in spec["locations"].items():
        if name in SALES:
            info = {**info, "type": SHUFFLE}
        elif info.get("type") in ("Scrub", "GrottoScrub") and not info.get("keep_vanilla"):
            info = {**info, "keep_vanilla": "scrub shuffle: repeat/rotating vendor, not a saved one-time family"}
        locations[name] = info
    spec = {**spec, "locations": locations}
    held = dict(settings.item_location_types)
    for item in CAPACITIES:
        held[item] = (SHUFFLE,) if item not in held else tuple(t for t in held[item] if t == SHUFFLE)
    settings = replace(settings, item_location_types=held)
    _, world = prepare(spec, settings)
    checks = tuple(
        name
        for name, loc in world.locations.items()
        if name in SALES and loc.vanilla is not None and not loc.n64_only and not loc.keep_vanilla
    )
    actors = item_actors.load()

    def step(placements: Mapping[str, str]) -> FileChanges:
        # Even an unchanged capacity placement must normalize both native tier
        # branches to the single fixed item represented in the pool.
        return changes({name: actors.actor(placements[name]) for name in checks})

    return spec, settings, step
