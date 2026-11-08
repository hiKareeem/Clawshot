"""Gossip Stones and the other hint givers: where they stand and how each picks its text.

**A stone's text is its placement name.** Every talking stone is an ``Obj_GossipStone_A_01`` actor with a ``Name``
(``GOSSIP_<AREA>_<NN>``) and no ``Dynamic`` parameters. Talking to one runs flow ``GossipStone``, entry ``Talk``; when
the stone speaks, the step is ``Npc_EventStarter.EventTalkWithInstanceNameLabel`` with ``MstxtName: GossipStone``: the
message whose label is the speaking actor's instance name, in ``EventFlowMsg/GossipStone.msbt`` of the language's
archive (``Mals/<language>.Product.110.sarc.zs``). So changing a stone's line is changing that one message; the flow
and the placement stay as they are. Child and adult files place each stone as two actors (two ``Hash`` values) with the
same name. One stone is placed in two areas' files: the Kokiri Forest files hold a copy of the Lost Woods bridge ledge
(``GOSSIP_LOST_WOOD_02``), the same stone in other coordinates.

**What the stone needs** is read from the flow, not assumed: :func:`talk_gates` lists the switch steps every path from
``Talk`` to the instance-name step passes, with the case it takes. In this game those are "the Mask of Truth is in the
pouch" and "the Mask of Truth is worn" (a Bool query's case 0 is true: ``03-game-data.md`` section 19); without the
mask the flow plays Navi's remarks instead.

:data:`STONE_LINKS` ties each stone to OoT Randomizer's hint stone of the same place (``LocationList.py`` at
``526b4c8d``), with the evidence; ``None`` for a stone OoT Randomizer does not have. :data:`HINT_GIVERS` lists the
other places a hint could be written, each a flow and the message labels it shows (``03-game-data.md`` section 22).
"""

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from clawshot.census.gifts import FLOW_VERSIONS, flow_files
from clawshot.census.scan import BANC_GLOB, EXCLUDED_AREAS, file_age, read_romfs_byml
from clawshot.formats import evfl, zsdic

STONE_ACTOR = "Obj_GossipStone_A_01"
SILENT_STONE_ACTOR = "Obj_GossipStone_A_02"  # Zora's Domain, adult: no name, no talk links
GOSSIP_FLOW = "GossipStone"
TALK_ENTRY = "Talk"
INSTANCE_TALK = "EventTalkWithInstanceNameLabel"
GOSSIP_MESSAGES = "EventFlowMsg/GossipStone.msbt"
MESSAGE_ARCHIVE = "Mals/{language}.Product.110.sarc.zs"
MASK_OF_TRUTH = "Armor_Child_Mask_Truth"
# Copies of one stone in the child and adult files stand within this distance of each other (Zora's Domain: 1 m).
SAME_STONE_DISTANCE = 2.0


class HintCensusError(ValueError):
    pass


@dataclass(frozen=True)
class GossipStone:
    """One talking stone: ``label`` is its placement ``Name`` and the label of its message; ``copies`` are its
    (placement file, ``Hash``) pairs; ``ages`` child, adult or both."""

    area: str
    label: str
    position: tuple[float, float, float]
    copies: tuple[tuple[str, int], ...]
    ages: str
    presence: tuple[str, ...]  # the Presence flags that show or hide it


@dataclass(frozen=True)
class TalkGate:
    """A switch step on the way to the stone's line, and the case that leads on."""

    event: str
    actor: str
    query: str
    params: tuple[tuple[str, object], ...]
    case: int


def _area(path: str) -> str:
    return PurePosixPath(path).parts[1]


def scan_stones(banc: Mapping[str, object]) -> list[GossipStone]:
    """The talking stones in parsed placement files (romfs path -> BYML tree), sorted by area and label.

    Copies with one name in one area are one stone when they stand within :data:`SAME_STONE_DISTANCE`; one name at
    two places in one area is an error (it would be two stones saying one line, which the data does not do)."""
    found: dict[tuple[str, str], list[tuple[str, Mapping]]] = {}
    for path in sorted(banc):
        area = _area(path)
        if area in EXCLUDED_AREAS:
            continue
        tree = banc[path]
        for actor in tree.get("Actors", []) if isinstance(tree, Mapping) else []:
            if actor["Gyaml"] != STONE_ACTOR:
                continue
            if "Name" not in actor:
                raise HintCensusError(f"{path}: {STONE_ACTOR} Hash {int(actor['Hash'])} has no Name")
            found.setdefault((area, str(actor["Name"])), []).append((path, actor))
    stones = []
    for (area, label), placed in sorted(found.items()):
        first = tuple(float(v) for v in placed[0][1]["Translate"])
        for path, actor in placed[1:]:
            where = tuple(float(v) for v in actor["Translate"])
            if math.dist(first, where) > SAME_STONE_DISTANCE:
                raise HintCensusError(f"{area} {label}: copies {first} and {where} ({path}) are not one stone")
        ages = {file_age(path) for path, _ in placed}
        stones.append(
            GossipStone(
                area=area,
                label=label,
                position=first,
                copies=tuple((path, int(actor["Hash"])) for path, actor in placed),
                ages="both" if ages >= {"child", "adult"} or "both" in ages else ages.pop(),
                presence=tuple(sorted({str(a["Presence"]["FlagName"]) for _, a in placed if "Presence" in a})),
            )
        )
    return stones


def _successors(event) -> list[tuple[int | None, int]]:
    """(case or None, next event) for each way out of a step inside one flowchart."""
    if isinstance(event, evfl.SwitchEvent | evfl.SubFlowSwitchEvent):
        return [(value, target) for value, target in event.cases]
    if isinstance(event, evfl.ForkEvent):
        return [(None, i) for i in event.forks] + [(None, event.join)]
    nxt = getattr(event, "next", evfl.NONE)
    return [] if nxt == evfl.NONE else [(None, nxt)]


def talk_gates(flowchart: evfl.Flowchart, entry: str = TALK_ENTRY, action: str = INSTANCE_TALK) -> list[TalkGate]:
    """The switch steps (with their case) that every path from ``entry`` to an ``action`` step passes.

    Raises :class:`HintCensusError` when no path reaches such a step."""
    start = flowchart.entry_point(entry).main_event
    paths: list[list[tuple[int, int | None]]] = []

    def walk(index: int, trail: list[tuple[int, int | None]], seen: frozenset[int]) -> None:
        if index == evfl.NONE or index in seen:
            return
        event = flowchart.events[index]
        if isinstance(event, evfl.ActionEvent) and flowchart.actors[event.actor].actions[event.action] == action:
            paths.append(trail)
            return
        for case, target in _successors(event):
            walk(target, [*trail, (index, case)], seen | {index})

    walk(start, [], frozenset())
    if not paths:
        raise HintCensusError(f"{flowchart.name}: no path from {entry} reaches {action}")
    common = set(paths[0])
    for trail in paths[1:]:
        common &= set(trail)
    gates = []
    for index, case in paths[0]:
        event = flowchart.events[index]
        if (index, case) not in common or case is None or not isinstance(event, evfl.SwitchEvent):
            continue
        actor = flowchart.actors[event.actor]
        params = tuple(sorted((k, v) for k, v in (event.params or {}).items()))
        gates.append(TalkGate(event.name, actor.name, actor.queries[event.query], params, case))
    return gates


def needs_mask_of_truth(gates: Iterable[TalkGate]) -> bool:
    """Whether the gates ask for the Mask of Truth worn (case 0, true, of the equip query)."""
    return any(
        gate.query == "EventQueryPlayerIsEquipArmor"
        and dict(gate.params).get("ArmorName") == MASK_OF_TRUTH
        and gate.case == 0
        for gate in gates
    )


def read_stones(romfs: str | Path) -> list[GossipStone]:
    """The talking stones in the dump at ``romfs`` (read only)."""
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    paths = sorted(p.relative_to(romfs).as_posix() for p in romfs.glob(BANC_GLOB))
    return scan_stones({path: read_romfs_byml(romfs, dicts, path) for path in paths})


def flow_path(romfs: str | Path, flow: str) -> str:
    """The romfs path of ``flow`` as the game loads it (``<flow>.<version>`` where the versions list names one)."""
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dicts, FLOW_VERSIONS)["Versions"].items()}
    return flow_files(romfs, versions)[flow]


def read_flow(romfs: str | Path, flow: str) -> evfl.Flowchart:
    """The flowchart of ``flow`` as the game loads it."""
    romfs = Path(romfs)
    path = flow_path(romfs, flow)
    chart = evfl.read(zsdic.Dictionaries.from_romfs(romfs).decompress(path, (romfs / path).read_bytes())).flowchart
    if chart is None:
        raise HintCensusError(f"{path} holds no flowchart")
    return chart


# --- links to OoT Randomizer ---------------------------------------------------------------------------------------

# (area, label) -> (OoT Randomizer hint stone or None, evidence). "pair"/"set": the stones share one OoT Randomizer
# region, and which name goes to which stone is not settled (only the label differs). Sources: the placement data
# (nearby actors, grotto rooms and covers; scratch E:/OOTRemake/work/r6-hints/stone_context.py, grotto_link.py),
# round 4's grotto findings (plans/rounds/r4-logic-child.md), and Zelda Central's remake guide
# https://zeldacentral.com/games/ocarina-of-time-remake/gossip-stones/ (facts only).
STONE_LINKS: dict[tuple[str, str], tuple[str | None, str]] = {
    ("DeathMountainCrater", "GOSSIP_DEATH_MOUNTAIN_CRATER_01"): (
        "DMC Gossip Stone",
        "upper crater, behind a WallCrack (OoT Randomizer: DMC Upper Local, has_explosives)",
    ),
    ("DeathMountainCrater", "GOSSIP_DEATH_MOUNTAIN_CRATER_02"): (
        "DMC Upper Grotto Gossip Stone",
        "grotto room with chest 1158729434763801603 (r4: DMC Upper Grotto Chest)",
    ),
    ("DeathMountainTrail", "GOSSIP_DEATH_MOUNTAIN_TRAIL_02"): ("DMT Gossip Stone", "summit, by Biggoron"),
    ("DeathMountainTrail", "GOSSIP_HYRULE_CASTLE_03"): (
        None,
        "grotto room with a cow, beside the storms grotto room 1154915296159103350 (Baby Dodongos, no stone: r4); "
        "N64's cow grotto has no stone and the remake's storms grotto has none",
    ),
    ("DesertColossus", "GOSSIP_DESERT_COLOSSUS_01"): ("Colossus Gossip Stone", "the area's only stone"),
    ("DodongoCavern", "GOSSIP_DODONGO_CAVERN_01"): ("Dodongos Cavern Gossip Stone", "room 1, behind a WallCrack"),
    ("GerudoValley", "GOSSIP_GERUDO_VALLEY_01"): ("GV Gossip Stone", "the area's only stone"),
    ("GoronCity", "GOSSIP_GORON_CITY_01"): ("GC Medigoron Gossip Stone", "beside Medigoron"),
    ("GoronCity", "GOSSIP_GORON_CITY_02"): (
        "GC Maze Gossip Stone",
        "among the maze's lift rocks, iron rocks, chest and Gold Skulltula",
    ),
    ("Graveyard", "GOSSIP_GRAVEYARD_01"): ("Graveyard Gossip Stone", "by the warp pad (Nocturne start)"),
    ("HyruleCastle", "GOSSIP_HYRULE_CASTLE_01"): ("HC Malon Gossip Stone", "beside child Malon and Talon"),
    ("HyruleCastle", "GOSSIP_HYRULE_CASTLE_02"): (
        "HC Rock Wall Gossip Stone",
        "the grounds' other open-air stone (Gold Skulltula and butterfly nearby)",
    ),
    ("HyruleCastle", "GOSSIP_HYRULE_FIELD_01"): (
        "HC Storms Grotto Gossip Stone",
        "grotto room under storms cover 13073548223054495027 (r4), with a WallCrack and a Gold Skulltula",
    ),
    ("HyruleField", "GOSSIP_HYRULE_FIELD_02"): (
        "HF Southeast Grotto Gossip Stone",
        "grotto room under the east cover at (180,156,190); Southeast or Near Market not settled (r4: one generic "
        "grotto fewer), both OoT Randomizer grotto regions entered by blasting",
    ),
    ("HyruleField", "GOSSIP_HYRULE_FIELD_03"): (
        "HF Open Grotto Gossip Stone",
        "grotto room under the wetlands cover 2786334400301738354 (r4: HF Open Grotto)",
    ),
    ("HyruleField", "GOSSIP_HYRULE_FIELD_04"): ("HF Cow Grotto Gossip Stone", "grotto room with the cow"),
    ("HyruleField", "GOSSIP_LAKE_HYLIA_01"): (
        "LH Gossip Stone (Southeast)",
        "set of three, all OoT Randomizer Lake Hylia",
    ),
    ("HyruleField", "GOSSIP_LAKE_HYLIA_02"): ("LH Lab Gossip Stone", "set of three, all OoT Randomizer Lake Hylia"),
    ("HyruleField", "GOSSIP_LAKE_HYLIA_03"): (
        "LH Gossip Stone (Southwest)",
        "set of three, all OoT Randomizer Lake Hylia",
    ),
    ("KakarikoVillage", "GOSSIP_DEATH_MOUNTAIN_TRAIL_01"): (
        None,
        "grotto room with a beehive and butterflies under cover 12611727494616924395; not an OoT Randomizer stone",
    ),
    ("KakarikoVillage", "GOSSIP_KAKARIKO_VILLAGE_01"): (
        "Kak Open Grotto Gossip Stone",
        "grotto room with a chest (r4: the open grotto's 5-rupee chest)",
    ),
    ("KokiriForest", "GOSSIP_KOKIRI_FOREST_01"): (
        "KF Gossip Stone",
        "beside the storms grotto cover (r4: the stone stands outside; the grotto room has none)",
    ),
    ("KokiriForest", "GOSSIP_KOKIRI_FOREST_03"): ("KF Deku Tree Gossip Stone (Left)", "pair before the Deku Tree"),
    ("KokiriForest", "GOSSIP_KOKIRI_FOREST_04"): ("KF Deku Tree Gossip Stone (Right)", "pair before the Deku Tree"),
    ("KokiriForest", "GOSSIP_LOST_WOOD_02"): (
        None,
        "the Lost Woods bridge stone as the Kokiri Forest files place it: the stone, the stick-bag scrub and chest "
        "4349272251343787229 stand at one offset (82, -20, 88) from the Lost Woods copies; see LostWood",
    ),
    ("LostWood", "GOSSIP_LOST_WOOD_02"): ("LW Gossip Stone", "open air by the bridge scrub (r2, r4)"),
    ("Market", "GOSSIP_HYRULE_MARKET_01"): (
        "ToT Gossip Stone (Left)",
        "set of four in a row outside the Temple of Time",
    ),
    ("Market", "GOSSIP_HYRULE_MARKET_02"): (
        "ToT Gossip Stone (Left-Center)",
        "set of four in a row outside the Temple of Time",
    ),
    ("Market", "GOSSIP_HYRULE_MARKET_03"): (
        "ToT Gossip Stone (Right-Center)",
        "set of four in a row outside the Temple of Time",
    ),
    ("Market", "GOSSIP_HYRULE_MARKET_04"): (
        "ToT Gossip Stone (Right)",
        "set of four in a row outside the Temple of Time",
    ),
    ("SacredForestMeadow", "GOSSIP_KOKIRI_FOREST_02"): (
        None,
        "remake-only, behind the Song of Time block with a chest (Zelda Central)",
    ),
    ("SacredForestMeadow", "GOSSIP_SACRED_FOREST_MEADOW_01"): (
        "SFM Maze Gossip Stone (Lower)",
        "pair in the maze (Mad Scrubs, Moblins)",
    ),
    ("SacredForestMeadow", "GOSSIP_SACRED_FOREST_MEADOW_02"): (
        "SFM Maze Gossip Stone (Upper)",
        "pair in the maze (Mad Scrubs, Moblins)",
    ),
    ("SacredForestMeadow", "GOSSIP_SACRED_FOREST_MEADOW_03"): (
        "SFM Saria Gossip Stone",
        "by Saria's stump and the Minuet warp pad (Zelda Central: on the way to the Forest Temple)",
    ),
    ("ZoraDomain", "GOSSIP_ZORA_DOMAIN_01"): ("ZD Gossip Stone", "the area's only talking stone (child and adult)"),
    ("ZoraFountain", "GOSSIP_ZORA_FOUNTAIN_01"): ("ZF Jabu Gossip Stone", "the fountain's open-air stone"),
    ("ZoraFountain", "GOSSIP_ZORA_FOUNTAIN_02"): (
        "ZF Fairy Gossip Stone",
        "by the fairy fountain's WallCrack and silver rock",
    ),
    ("ZoraRiver", "GOSSIP_LOST_WOOD_01"): (
        None,
        "grotto room under storms cover 5489068764052953067 (r4: ZR Storms Grotto); not an OoT Randomizer stone",
    ),
    ("ZoraRiver", "GOSSIP_ZORA_RIVER_01"): ("ZR Near Grottos Gossip Stone", "by the river's heart piece and holes"),
    ("ZoraRiver", "GOSSIP_ZORA_RIVER_02"): (
        "ZR Open Grotto Gossip Stone",
        "grotto room with chest and cucco (r4: the open grotto)",
    ),
    ("ZoraRiver", "GOSSIP_ZORA_RIVER_03"): ("ZR Near Domain Gossip Stone", "upper river, by the Lost Woods shortcut"),
}

# OoT Randomizer hint stones with no stone in the remake, and why.
OOTR_STONES_MISSING: dict[str, str] = {
    "KF Storms Grotto Gossip Stone": "the grotto room holds the scrub trio and a chest, no stone (r4)",
    "LW Near Shortcuts Grotto Gossip Stone": "the room under the boulder holds no stone (r4)",
    "HF Near Market Grotto Gossip Stone": "one generic grotto fewer in Hyrule Field (r4); see GOSSIP_HYRULE_FIELD_02",
    "DMT Storms Grotto Gossip Stone": "the storms grotto holds Baby Dodongos, bomb flowers and rupees (r4)",
}

# The remake-only stones (``None`` in :data:`STONE_LINKS`): their names in the world, where
# ``data/world/remake/hint_stones.toml`` gives each a region and a rule.
REMAKE_STONES: dict[tuple[str, str], str] = {
    ("SacredForestMeadow", "GOSSIP_KOKIRI_FOREST_02"): "SFM Song of Time Clearing Gossip Stone",
    ("KakarikoVillage", "GOSSIP_DEATH_MOUNTAIN_TRAIL_01"): "Kak Bomb Grotto Gossip Stone",
    ("ZoraRiver", "GOSSIP_LOST_WOOD_01"): "ZR Storms Grotto Gossip Stone",
    ("DeathMountainTrail", "GOSSIP_HYRULE_CASTLE_03"): "DMT Cow Grotto Gossip Stone",
}


def stone_labels() -> dict[str, str]:
    """Each Gossip Stone of the world (its location name) to the message label it speaks, one label per stone.

    A census entry linked to nothing that is not a remake-only stone is a second placement of a stone listed in
    another area (the Kokiri Forest files' copy of the Lost Woods bridge stone): it adds no stone."""
    named = {key: link or REMAKE_STONES.get(key) for key, (link, _evidence) in STONE_LINKS.items()}
    labels: dict[str, str] = {}
    for (area, label), name in named.items():
        if name is None:
            if not any(other_label == label and other for (_, other_label), other in named.items()):
                raise HintCensusError(f"{area} {label}: neither linked, remake-only nor a copy of a linked stone")
            continue
        if name in labels or label in labels.values():
            raise HintCensusError(f"{area} {label}: stone {name!r} or label {label} given twice")
        labels[name] = label
    return labels


@dataclass(frozen=True)
class HintGiver:
    """Another place a hint could be written: ``flow`` shows ``labels`` of ``messages`` (``EventFlowMsg/...``)."""

    name: str
    flow: str
    messages: str
    labels: tuple[str, ...]
    ootr_hint: str  # the OoT Randomizer hint it would carry, or "" when none fits


HINT_GIVERS: tuple[HintGiver, ...] = (
    HintGiver(
        "Skulltula House: the line per token count (10, 20, 30, 40, 50, 100); it names no reward",
        "GatheringTokenGold",
        "EventFlowMsg/Npc_SkullDad.msbt",
        ("Talk_28", "Talk_23", "Talk_24", "Talk_25", "Talk_26", "Talk_27"),
        "10/20/30/40/50/100 Skulltulas Reward Hint",
    ),
    HintGiver(
        "Dampe's diary, adult: the page about his own grave",
        "Diary_Hylia_Dampe_Adult",
        "EventFlowMsg/Diary_Hylia_Dampe_Adult.msbt",
        ("Talk_03",),
        "Dampe Diary Hint",
    ),
    HintGiver(
        "Sheik, adult: the lines sending Link to the Sheikah's tool in Kakariko",
        "Npc_Hylia_Sheik_Adult",
        "EventFlowMsg/Npc_Hylia_Sheik_Adult.msbt",
        ("Talk_01", "Talk_03"),
        "",
    ),
)
