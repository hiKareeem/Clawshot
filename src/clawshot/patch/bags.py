"""An item brings its first bag: Deku Sticks and Deku Nuts their base capacity (``Item_StickBag_Small`` = 10 sticks,
``Item_NutBag_Small`` = 20 nuts), the Slingshot its bullet bag (``Item_BulletBag_Small``, 30 seeds) and the Bow its
quiver (``Item_Quiver_Small``, 30 arrows). Without one, the ammo is not held. Ammo alone brings no bag: arrows and
seeds wait for the Bow and the Slingshot (mysterypaint, 2026-11-12); bombs bring the Bomb Bag natively.

The Slingshot and the Bow (``Item_Range_*`` from a chest, ``Weapon_Range_*`` given by name) name no bag in their
pouch rows and no event flow gives these bags; a Slingshot given without one came with no bullet bag (play,
2026-11-12).

The pouch rows (``RSDB/PouchActorInfo``) of ``Item_DekuStick`` and ``Item_DekuNut`` name these bags as their
``SmallBagActor`` with ``IsAbleToGetBagIfGet``, and ``plans/03-game-data.md`` section 24 inferred from them that a stick
or nut from a chest brings the bag, as the Bomb Bag comes with bombs (seen in game). In play it does not (reported by
mysterypaint, 2026-11-12: sticks and nuts from chests and from the multiworld leave Link without the bag). No event flow
gives these bags (only ``Npc_Goron_006_Child`` gives ``Item_BombBag_Small``, by name), so the fix does what that flow
does instead of relying on the row.

Every chest, NPC gift and pick-up window gives through one action, ``GetPouchContent`` Event0
(``PouchSystemActor.EventTriggerAddOrRemovePouchContent``, the content in the ``ActorName`` argument). Before it,
:func:`patch_flow` adds: name the content in ``UI_MessageTargetActorName`` (the get window's own String64, as
``clawshot.patch.getitem`` does), and when it is a stick or nut item and Link holds no bag of that kind
(``PouchSystemActor.EventQueryIsExistInPouch`` on each tier, as the Goron's flow asks), add the small bag, then go on to
the native add. A bag already held is never replaced, so a capacity upgrade found first stays.
"""

import copy
from collections.abc import Mapping, Sequence
from pathlib import Path

from clawshot.census.hints import flow_path
from clawshot.formats import evfl
from clawshot.patch.plan import PatchError

FLOW = "GetPouchContent"
MESSAGE_TARGET = "UI_MessageTargetActorName"
PREFIX = "Clawshot_Bag_"

# Contents that are sticks or nuts (base pick-ups, chest bundles, shop bundles), and their bags, smallest first.
FAMILIES: Mapping[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "sticks": (
        (
            "Item_DekuStick",
            "Item_DekuStickBundle_Small",
            "Obj_DekuStick",
            "Shop_DekuStick",
            "Shop_DekuStickBundle_Medium",
        ),
        ("Item_StickBag_Small", "Item_StickBag_Medium", "Item_StickBag_Large"),
    ),
    "nuts": (
        ("Item_DekuNut", "Obj_DekuNut", "TBox_DekuNutBundle", "Shop_DekuNutBundle_01", "Shop_DekuNutBundle_02"),
        ("Item_NutBag_Small", "Item_NutBag_Medium", "Item_NutBag_Large"),
    ),
    "slingshot": (
        ("Item_Range_SlingShot", "Weapon_Range_SlingShot"),
        ("Item_BulletBag_Small", "Item_BulletBag_Medium", "Item_BulletBag_Large"),
    ),
    "bow": (
        ("Item_Range_Bow", "Weapon_Range_Bow"),
        ("Item_Quiver_Small", "Item_Quiver_Medium", "Item_Quiver_Large"),
    ),
}


def _index(names: list[str], name: str) -> int:
    if name not in names:
        names.append(name)
    return names.index(name)


def patch_flow(flowchart: evfl.Flowchart, families: Mapping[str, tuple[Sequence[str], Sequence[str]]] = FAMILIES):
    """Edit ``GetPouchContent`` in place (see the module). Returns the index of the first new event."""
    if flowchart.name != FLOW:
        raise PatchError(f"not the {FLOW} flow: {flowchart.name}")
    if any(event.name.startswith(PREFIX) for event in flowchart.events):
        raise PatchError(f"{FLOW}: bag gates already added")
    actors = {actor.name: i for i, actor in enumerate(flowchart.actors) if not actor.secondary_name}
    for needed in ("PouchSystemActor", "GameDataActor"):
        if needed not in actors:
            raise PatchError(f"{FLOW}: no {needed}")
    pouch, game_data = actors["PouchSystemActor"], actors["GameDataActor"]
    add = flowchart.events[0] if flowchart.events else None
    if not (
        isinstance(add, evfl.ActionEvent)
        and add.actor == pouch
        and flowchart.actors[pouch].actions[add.action] == "EventTriggerAddOrRemovePouchContent"
        and (add.params or {}).get("Actor") == evfl.Argument("ActorName")
    ):
        raise PatchError(f"{FLOW}: Event0 is no longer the content's AddOrRemovePouchContent: {add}")
    target = 0
    original = len(flowchart.events)
    pouch_actor, gd_actor = flowchart.actors[pouch], flowchart.actors[game_data]
    is_in_pouch = _index(pouch_actor.queries, "EventQueryIsExistInPouch")
    add_action = pouch_actor.actions.index("EventTriggerAddOrRemovePouchContent")
    set_string = _index(gd_actor.actions, "EventTriggerSetGameDataString64")
    is_string = _index(gd_actor.queries, "EventQueryIsGameDataString64")

    def append(event) -> int:
        event.name = f"{PREFIX}{len(flowchart.events)}"
        flowchart.events.append(event)
        return len(flowchart.events) - 1

    otherwise = target
    for family in reversed(list(families)):
        contents, bags = families[family]
        give_params = copy.deepcopy(add.params)
        give_params.update({"Actor": bags[0], "Num": 1, "IsSetMessageTargetActorName": False, "IsGetEvent": False})
        give = append(evfl.ActionEvent("", pouch, add_action, target, give_params))
        # Ask for each tier, largest first: held -> the native add; none held -> the small bag first.
        check = give
        for bag in bags:
            check = append(
                evfl.SwitchEvent("", pouch, is_in_pouch, [(0, target), (1, check)], {"Num": 1, "Actor": bag})
            )
        for content in reversed(contents):
            otherwise = append(
                evfl.SwitchEvent(
                    "",
                    game_data,
                    is_string,
                    [(0, check), (1, otherwise)],
                    {"GameDataName": MESSAGE_TARGET, "Index": -1, "Value": content},
                )
            )
    first = append(
        evfl.ActionEvent(
            "",
            game_data,
            set_string,
            otherwise,
            {"GameDataName": MESSAGE_TARGET, "Index": -1, "Value": evfl.Argument("ActorName")},
        )
    )
    # Every way into the native add now comes through the gates (the new events' own edges excepted).
    for event in flowchart.events[:original]:
        if getattr(event, "next", None) == target:
            event.next = first
        if isinstance(event, evfl.ForkEvent):
            event.forks = [first if i == target else i for i in event.forks]
        if isinstance(event, (evfl.SwitchEvent, evfl.SubFlowSwitchEvent)):
            event.cases = [(value, first if i == target else i) for value, i in event.cases]
    for entry in flowchart.entry_points:
        if entry.main_event == target:
            entry.main_event = first
    return first


def transform(data: bytes) -> bytes:
    """The ``GetPouchContent`` flow file (decompressed) with :func:`patch_flow` applied, read back checked."""
    document = evfl.read(data)
    if document.flowchart is None:
        raise PatchError(f"the {FLOW} flow holds no flowchart")
    patch_flow(document.flowchart)
    written = evfl.write(document)
    if evfl.read(written) != document:
        raise PatchError(f"{FLOW}: the written flow does not read back as the edited flow")
    return written


def changes(romfs: str | Path) -> dict:
    """The file change of this fix, for ``clawshot.patch.write``."""
    return {flow_path(romfs, FLOW): transform}
