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

``GetPouchContent`` Event0 covers chests and most gifts, but ``Dm_SY_GetInEvent`` also grants directly
in Goron hand-overs, scrub purchases and its shield helper. Shuffled source flows can give a literal actor
directly too. Each positive grant gets the same missing-bag guard; removals and ammo-only refills do not.
Dynamic names use ``UI_MessageTargetActorName`` to select the family; literal names select it at
compile time without touching message state. Every bag tier is checked before adding a missing small
bag. Existing capacity, original quantity, message, equip and get-event flags survive. Literal source
grants are guarded after their gift rewrites; shared flows after named-key compilation.
"""

import copy
from collections.abc import Mapping, Sequence
from pathlib import Path

from clawshot.census.hints import flow_path
from clawshot.formats import evfl
from clawshot.patch.plan import PatchError

FLOW = "GetPouchContent"
HANDOVER_FLOW = "Dm_SY_GetInEvent"
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
    pouch = actors["PouchSystemActor"]
    add = flowchart.events[0] if flowchart.events else None
    if not (
        isinstance(add, evfl.ActionEvent)
        and add.actor == pouch
        and flowchart.actors[pouch].actions[add.action] == "EventTriggerAddOrRemovePouchContent"
        and (add.params or {}).get("Actor") == evfl.Argument("ActorName")
    ):
        raise PatchError(f"{FLOW}: Event0 is no longer the content's AddOrRemovePouchContent: {add}")
    return _guard_grant(flowchart, 0, families)


def _guard_grant(
    flowchart: evfl.Flowchart, target: int, families: Mapping[str, tuple[Sequence[str], Sequence[str]]] = FAMILIES
) -> int:
    add = flowchart.events[target]
    assert isinstance(add, evfl.ActionEvent) and add.params is not None
    prefix = f"{PREFIX}{add.name}_"
    if any(event.name.startswith(prefix) for event in flowchart.events):
        raise PatchError(f"{flowchart.name}/{add.name}: bag gates already added")
    pouch = add.actor
    requested = add.params["Actor"]
    dynamic = isinstance(requested, evfl.Argument)
    original = len(flowchart.events)
    pouch_actor = flowchart.actors[pouch]
    is_in_pouch = _index(pouch_actor.queries, "EventQueryIsExistInPouch")
    add_action = pouch_actor.actions.index("EventTriggerAddOrRemovePouchContent")
    if dynamic:
        game_data = next(
            (
                i
                for i, actor in enumerate(flowchart.actors)
                if actor.name == "GameDataActor" and not actor.secondary_name
            ),
            None,
        )
        if game_data is None:
            game_data = len(flowchart.actors)
            flowchart.actors.append(evfl.Actor("GameDataActor"))
        gd_actor = flowchart.actors[game_data]
        set_string = _index(gd_actor.actions, "EventTriggerSetGameDataString64")
        is_string = _index(gd_actor.queries, "EventQueryIsGameDataString64")

    def append(event) -> int:
        event.name = f"{prefix}{len(flowchart.events)}"
        flowchart.events.append(event)
        return len(flowchart.events) - 1

    otherwise = target
    for family in reversed(list(families)):
        contents, bags = families[family]
        if not dynamic and requested not in contents:
            continue
        give_params = copy.deepcopy(add.params)
        give_params.update(
            {
                "Actor": bags[0],
                "Num": 1,
                "IsEquipDIrect": False,
                "IsSetMessageTargetActorName": False,
                "IsGetEvent": False,
            }
        )
        give = append(evfl.ActionEvent("", pouch, add_action, target, give_params))
        # Ask for each tier, largest first: held -> the native add; none held -> the small bag first.
        check = give
        for bag in bags:
            check = append(
                evfl.SwitchEvent("", pouch, is_in_pouch, [(0, target), (1, check)], {"Num": 1, "Actor": bag})
            )
        if not dynamic:
            otherwise = check
            break
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
    first = otherwise
    if dynamic:
        first = append(
            evfl.ActionEvent(
                "",
                game_data,
                set_string,
                otherwise,
                {"GameDataName": MESSAGE_TARGET, "Index": -1, "Value": requested},
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


def patch_grants(flowchart: evfl.Flowchart, *, literal_only: bool = False) -> None:
    """Guard positive pouch additions, using each action's own actor argument or literal."""
    targets = []
    for index, event in enumerate(flowchart.events):
        if not isinstance(event, evfl.ActionEvent) or not event.params:
            continue
        actor = flowchart.actors[event.actor]
        if actor.name != "PouchSystemActor" or actor.actions[event.action] != "EventTriggerAddOrRemovePouchContent":
            continue
        content = event.params.get("Actor")
        if isinstance(content, evfl.Argument):
            if literal_only:
                continue
        elif not any(content in contents for contents, _ in FAMILIES.values()):
            continue
        amount = event.params.get("Num")
        if isinstance(amount, evfl.Argument):
            raise PatchError(f"{flowchart.name}/{event.name}: cannot classify grant quantity {amount!r}")
        if isinstance(amount, int) and amount > 0:
            targets.append(index)
    for target in targets:
        _guard_grant(flowchart, target)


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


def handover_transform(data: bytes) -> bytes:
    """Guard direct hand-overs, including cloned grants introduced by earlier gift transforms."""
    document = evfl.read(data)
    if document.flowchart is None or document.flowchart.name != HANDOVER_FLOW:
        raise PatchError(f"the {HANDOVER_FLOW} file holds no flowchart of that name")
    patch_grants(document.flowchart)
    written = evfl.write(document)
    if evfl.read(written) != document:
        raise PatchError(f"{HANDOVER_FLOW}: the written flow does not read back as the edited flow")
    return written


def changes(romfs: str | Path) -> dict:
    """Shared grant transforms, composed after source gifts and named-key compilation."""
    return {flow_path(romfs, FLOW): transform, flow_path(romfs, HANDOVER_FLOW): handover_transform}
