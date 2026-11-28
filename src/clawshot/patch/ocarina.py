"""Keep Time selected after a genuine Fairy receipt (issue #34).

The native Ocarina special deal auto-equips even with IsEquipDIrect=false.
Leave every pouch add and its parameters intact; restore only EquipOcarina when
Time remains in the pouch. The shared helper runs before the original cleanup
or source once-write. This is not a progressive item or an old-save repair.
"""

import copy
from collections.abc import Sequence
from pathlib import Path

from clawshot.census.gifts import reachable
from clawshot.formats import evfl, zsdic
from clawshot.patch import bags, keys
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

FAIRY = "Item_Ocarina_Fairy"
TIME = "Item_Ocarina_Time"
EQUIPPED = "PlayerStatus.EquipOcarina"
HELPER = "ClawshotOcarinaKeepTime"
_PREFIX = "ClawshotOcarina_"
# Other direct Fairy rewards can be introduced by earlier gift transforms.
_NATIVE_FLOWS = (keys.POUCH, "Dm_SY_GetInEvent", "Dm_Kokiri_0155", "Dm_MelodyGet_Time")


def _targets(chart: evfl.Flowchart) -> list[int]:
    result = []
    for index, event in enumerate(chart.events):
        if not isinstance(event, evfl.ActionEvent) or not event.params:
            continue
        actor = chart.actors[event.actor]
        if actor.name != "PouchSystemActor" or actor.actions[event.action] != "EventTriggerAddOrRemovePouchContent":
            continue
        content, amount = event.params.get("Actor"), event.params.get("Num")
        if content != FAIRY and not isinstance(content, evfl.Argument):
            continue
        if type(amount) is not int:
            raise PatchError(f"{chart.name}/{event.name}: unclassified ocarina grant amount {amount!r}")
        if amount <= 0:
            continue
        # These native argument-driven grants set the same UI identity used by
        # the get window and existing bag guards. Never guess a stale identity.
        if isinstance(content, evfl.Argument) and event.params.get("IsSetMessageTargetActorName") is not True:
            raise PatchError(f"{chart.name}/{event.name}: ocarina grant has no current message identity")
        result.append(index)
    return result


def _add_helper(chart: evfl.Flowchart) -> None:
    if any(entry.name == HELPER for entry in chart.entry_points):
        raise PatchError(f"{chart.name}: ocarina helper already exists")
    pouch, held = keys._operation(chart, "PouchSystemActor", "queries", "EventQueryIsExistInPouch")
    game, set_string = keys._operation(chart, "GameDataActor", "actions", "EventTriggerSetGameDataString64")
    system, wait = keys._operation(chart, "GameSystemActor", "actions", "EventWait")
    ui, sync = keys._operation(chart, "UISystemActor", "actions", "EventTriggerSyncPlayerEquipmentAndPouch")
    start = len(chart.events)
    chart.events.extend(
        [
            evfl.SwitchEvent(
                HELPER + "Owned", pouch, held, [(0, start + 1), (1, evfl.NONE)], {"Actor": TIME, "Num": 1}
            ),
            evfl.ActionEvent(
                HELPER + "Select",
                game,
                set_string,
                start + 2,
                {"GameDataName": EQUIPPED, "Index": -1, "Value": TIME},
            ),
            evfl.ActionEvent(HELPER + "Commit", system, wait, start + 3, {"Frames": 1, "IsWaitEnd": True}),
            evfl.ActionEvent(HELPER + "Sync", ui, sync),
        ]
    )
    chart.entry_points.append(evfl.EntryPoint(HELPER, start))


def patch_grants(chart: evfl.Flowchart) -> None:
    """Append receipt continuations, preserving the original grant and all its incoming edges."""
    if any(event.name.startswith(_PREFIX) for event in chart.events):
        raise PatchError(f"{chart.name}: ocarina receipts already patched")
    calls = []
    for target in _targets(chart):
        grant = chart.events[target]
        onward = grant.next
        call = len(chart.events)
        chart.events.append(
            evfl.SubFlowEvent(
                f"{_PREFIX}{grant.name}_KeepTime", "" if chart.name == keys.POUCH else keys.POUCH, HELPER, onward
            )
        )
        calls.append(call)
        grant.next = call
        if isinstance(grant.params["Actor"], evfl.Argument):
            game, is_string = keys._operation(chart, "GameDataActor", "queries", "EventQueryIsGameDataString64")
            grant.next = len(chart.events)
            chart.events.append(
                evfl.SwitchEvent(
                    f"{_PREFIX}{grant.name}_IsFairy",
                    game,
                    is_string,
                    [(0, call), (1, onward)],
                    {"GameDataName": bags.MESSAGE_TARGET, "Index": -1, "Value": FAIRY},
                )
            )
    for entry in chart.entry_points:
        seen = reachable(chart, entry.main_event)
        entry.sub_flow_events.extend(call for call in calls if call in seen)


def _transform(before: evfl.EventFlowFile, after: evfl.EventFlowFile):
    encoded = evfl.write(after)
    if evfl.read(encoded) != after:
        raise PatchError(f"{after.name}: ocarina receipts do not read back")

    def transform(data: bytes) -> bytes:
        if evfl.read(data) != before:
            raise PatchError(f"{before.name}: ocarina receipt source changed after binding")
        return encoded

    return transform


def changes(romfs: str | Path, *, prior_changes: Sequence[FileChanges] = ()) -> FileChanges:
    """Compose last, after gifts, named/progressive grants and bag guards; never change placement."""
    root = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(root)
    paths = {keys.flow_path(name) for name in _NATIVE_FLOWS}
    paths.update(
        path
        for step in prior_changes
        for path in step
        if path.startswith("Event/EventFlow/") and path.endswith(".bfevfl.zs")
    )

    def read(path):
        data = dictionaries.decompress(path, (root / path).read_bytes())
        for step in prior_changes:
            if path in step:
                data = step[path](data)
        document = evfl.read(data)
        if document.flowchart is None and path in native:
            raise PatchError(f"{path}: ocarina receipt source is not a flowchart")
        return document

    native = {keys.flow_path(name) for name in _NATIVE_FLOWS}
    # A changed timeline (an event prop shown through a container, event-items) holds no grant to bind.
    originals = {path: doc for path in sorted(paths) if (doc := read(path)).flowchart is not None}
    pouch_path = keys.flow_path(keys.POUCH)
    changed = copy.deepcopy(originals[pouch_path])
    _add_helper(changed.flowchart)
    patch_grants(changed.flowchart)
    result = {pouch_path: _transform(originals[pouch_path], changed)}
    for path, original in originals.items():
        if path == pouch_path or not _targets(original.flowchart):
            continue
        changed = copy.deepcopy(original)
        patch_grants(changed.flowchart)
        result[path] = _transform(original, changed)
    return result
