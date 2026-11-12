"""Small keys anywhere: only small keys leave their dungeon, and only into chests; a key outside its dungeon's Banc
area is a named key, whose chest changes even when it already holds the generic small key, and whose grant binding
is written over exactly the event state the plan classified. Synthetic worlds, census and placement files."""

import copy
from dataclasses import replace

import pytest

from clawshot.census import definitions as census_definitions
from clawshot.census.definitions import Definition
from clawshot.census.scan import CHEST, Location
from clawshot.formats import byml, rstb, zsdic
from clawshot.formats.byml import F32, U32, U64
from clawshot.generate import Seed, Settings, generate
from clawshot.generate.fill import SMALL_KEY, allowed, is_restricted
from clawshot.patch import events as chest_events
from clawshot.patch import items as item_actors
from clawshot.patch.key_targets import TARGETS
from clawshot.patch.plan import ChestChange, Links, PatchError, Plan, link, make_plan, restrict_key_openings
from clawshot.patch.write import patch_tree, write
from clawshot.world import Search, build_world, load_spec

KF_CHILD = "Banc/KokiriForest/KokiriForest_Child_Static.bcett.byml.zs"
KF_ADULT = "Banc/KokiriForest/KokiriForest_Adult_Static.bcett.byml.zs"
FOREST = "Banc/ForestTemple/ForestTemple_Static.bcett.byml.zs"
FIRE = "Banc/FireTemple/FireTemple_Static.bcett.byml.zs"
COLOSSUS = "Banc/DesertColossus/DesertColossus_Adult_Static.bcett.byml.zs"
TEMPLE = "Banc/Temple/Temple_Static.bcett.byml.zs"

FIELD_CHEST = 301
TWIN_CHILD, TWIN_ADULT = 302, 303  # one check under two Hashes, one in each age's file
KEPT_CHEST = 304  # an override that stays (keep)
STORY_CHEST = 305  # an override tied to its vanilla item (remove)
FOREST_KEY_CHEST = 401
FIRE_KEY_CHEST, FIRE_MAP_CHEST = 501, 502
HAND_CHEST = 601  # a Spirit Temple check in the Colossus's Banc, as the two hand chests are
TEMPLE_CHEST = 701  # a dungeon with logic small keys but no named target

FOREST_KEY = "Small Key (Forest Temple)"
FIRE_KEY = "Small Key (Fire Temple)"
SPIRIT_KEY = "Small Key (Spirit Temple)"
TEMPLE_KEY = "Small Key (Temple)"
FIRE_BOSS_KEY = "Boss Key (Fire Temple)"
FIRE_MAP = "Map (Fire Temple)"
FIRE_COMPASS = "Compass (Fire Temple)"
KEY_ACTOR = "Item_Dungeon_SmallKey"
RUPEE = "TBox_Rupee_Blue"

TABLE = item_actors.loads(
    f"""
[items]
"Sword" = {{ actor = "Item_Sword" }}
"Rupees (5)" = {{ actor = "{RUPEE}" }}
"{FOREST_KEY}" = {{ actor = "{KEY_ACTOR}" }}
"{FIRE_KEY}" = {{ actor = "{KEY_ACTOR}" }}
"{SPIRIT_KEY}" = {{ actor = "{KEY_ACTOR}" }}
"{TEMPLE_KEY}" = {{ actor = "{KEY_ACTOR}" }}
"{FIRE_BOSS_KEY}" = {{ actor = "Item_Dungeon_BossKey" }}
"{FIRE_MAP}" = {{ actor = "Item_Dungeon_Map" }}
"{FIRE_COMPASS}" = {{ actor = "Item_Dungeon_Compass" }}
"""
)

EVENTS = chest_events.loads(
    """
[event.Story_GetSword]
flow = "Story:GetSword"
patch = "remove"
does = "the chest event, then a sword cutscene"
story_state = "nothing to restore"

[event.House_NaviChatOff]
flow = "Small:Success_House"
patch = "keep"
does = "sets a flag, then the default event"
"""
)


def check(vanilla: str, kind: str = "Chest", **extra) -> dict:
    return {"rule": "True", "type": kind, "vanilla": vanilla, **extra}


def world_spec() -> dict:
    """An overworld field, two keyed dungeons with named targets, the Spirit Temple's hand checks standing in the
    Colossus's Banc and a keyed dungeon without a target."""
    return {
        "start": "Field",
        "goal": "True",
        "items": {
            "Sword": {},
            "Rupees (5)": {"class": "normal"},
            FOREST_KEY: {"type": "SmallKey"},
            FIRE_KEY: {"type": "SmallKey"},
            SPIRIT_KEY: {"type": "SmallKey"},
            TEMPLE_KEY: {"type": "SmallKey"},
            FIRE_BOSS_KEY: {"type": "BossKey"},
            FIRE_MAP: {"type": "Map", "class": "priority"},
            FIRE_COMPASS: {"type": "Compass", "class": "priority"},
        },
        "helpers": {},
        "settings": {},
        "regions": [
            {
                "name": "Field",
                "area": "KokiriForest",
                "locations": {
                    "Field Chest": check("Rupees (5)"),
                    "Twin Chest": check("Rupees (5)"),
                    "Kept Chest": check("Rupees (5)"),
                    "Story Chest": check("Sword"),
                    "Field Floor": check("Rupees (5)", "Freestanding"),
                },
                "exits": {"Forest Lobby": "True", "Fire Lobby": "True", "Spirit Hand": "True", "Temple Hall": "True"},
            },
            {
                "name": "Forest Lobby",
                "area": "ForestTemple",
                "dungeon": "Forest Temple",
                "locations": {
                    "Forest Key Chest": check(FOREST_KEY),
                    "Forest Floor": check("Rupees (5)", "Freestanding"),
                },
            },
            {
                "name": "Fire Lobby",
                "area": "FireTemple",
                "dungeon": "Fire Temple",
                "locations": {"Fire Key Chest": check(FIRE_KEY), "Fire Map Chest": check(FIRE_MAP)},
            },
            {
                "name": "Spirit Hand",
                "area": "SpiritTemple",
                "dungeon": "Spirit Temple",
                "locations": {
                    "Spirit Hand Chest": check("Rupees (5)", area="DesertColossus"),
                    "Spirit Hand Floor": check("Rupees (5)", "Freestanding", area="DesertColossus"),
                },
            },
            {
                "name": "Temple Hall",
                "area": "Temple",
                "dungeon": "Temple",
                "locations": {"Temple Chest": check("Rupees (5)")},
            },
        ],
    }


def census_location(
    actor_hash: int,
    area: str,
    files: tuple[str, ...],
    item: str,
    event: str | None = None,
    gyaml: str = "Obj_TBox_A_01",
) -> Location:
    return Location(
        id=actor_hash,
        kind=CHEST,
        area=area,
        room=None,
        files=files,
        ages="both",
        position=(0.0, 0.0, 0.0),
        actor=gyaml,
        vanilla_item=item,
        event=event,
        has_save_flag=True,
    )


CHESTS = [
    ("Field Chest", census_location(FIELD_CHEST, "KokiriForest", (KF_ADULT, KF_CHILD), RUPEE)),
    ("Twin Chest", census_location(TWIN_CHILD, "KokiriForest", (KF_CHILD,), RUPEE)),
    ("Twin Chest", census_location(TWIN_ADULT, "KokiriForest", (KF_ADULT,), RUPEE)),
    ("Kept Chest", census_location(KEPT_CHEST, "KokiriForest", (KF_ADULT, KF_CHILD), RUPEE, "House_NaviChatOff")),
    ("Story Chest", census_location(STORY_CHEST, "KokiriForest", (KF_ADULT, KF_CHILD), "Item_Sword", "Story_GetSword")),
    ("Forest Key Chest", census_location(FOREST_KEY_CHEST, "ForestTemple", (FOREST,), KEY_ACTOR)),
    ("Fire Key Chest", census_location(FIRE_KEY_CHEST, "FireTemple", (FIRE,), KEY_ACTOR)),
    ("Fire Map Chest", census_location(FIRE_MAP_CHEST, "FireTemple", (FIRE,), "Item_Dungeon_Map")),
    ("Spirit Hand Chest", census_location(HAND_CHEST, "DesertColossus", (COLOSSUS,), RUPEE, gyaml="Obj_TBox_A_02")),
    ("Temple Chest", census_location(TEMPLE_CHEST, "Temple", (TEMPLE,), RUPEE)),
]
CENSUS = [loc for _, loc in CHESTS]
DEFINITIONS = [Definition(loc.id, loc.kind, loc.area, name, loc.vanilla_item, name) for name, loc in CHESTS]

VANILLA = {
    "Field Chest": "Rupees (5)",
    "Twin Chest": "Rupees (5)",
    "Kept Chest": "Rupees (5)",
    "Story Chest": "Sword",
    "Field Floor": "Rupees (5)",
    "Forest Key Chest": FOREST_KEY,
    "Forest Floor": "Rupees (5)",
    "Fire Key Chest": FIRE_KEY,
    "Fire Map Chest": FIRE_MAP,
    "Spirit Hand Chest": "Rupees (5)",
    "Spirit Hand Floor": "Rupees (5)",
    "Temple Chest": "Rupees (5)",
}


@pytest.fixture
def world():
    return build_world(world_spec())


@pytest.fixture
def links(world):
    return link(world, [name for name, loc in world.locations.items() if loc.type == "Chest"], DEFINITIONS, CENSUS)


def plan_for(world, links, mode: str, moved: dict[str, str]) -> Plan:
    placements = {**VANILLA, **moved}
    seed = Seed(world, 1, Settings(dungeon_items=mode), placements, list(world.locations), [list(placements)])
    return make_plan(seed, links, TABLE, EVENTS)


def rows(plan: Plan) -> list[tuple]:
    return [(c.location, c.id, c.files, c.old_actor, c.new_actor, c.named_key) for c in plan.changes]


def bound(plan: Plan) -> Plan:
    """The plan as ``clawshot.patch.keys`` hands it on: each named key bound to its target's (synthetic) event."""
    return replace(
        plan,
        changes=[replace(c, key_event=f"Bind_{c.named_key}") if c.named_key else c for c in plan.changes],
    )


# --------------------------------------------------------------------------------------------------------------
# Targets


def test_targets_cover_every_logic_small_key_dungeon_and_exclude_fortress_keys():
    world = build_world(load_spec())
    keyed = {item.dungeon for item in world.items.values() if item.type == SMALL_KEY and item.dungeon is not None}
    assert set(TARGETS) == keyed
    assert world.items["Small Key (Thieves Hideout)"].dungeon is None  # the fortress keys stay as they are
    chest_areas = {d.area for d in census_definitions.load() if d.kind == CHEST}
    assert all(target.id in chest_areas for target in TARGETS.values())


# --------------------------------------------------------------------------------------------------------------
# The fill


def test_anywhere_releases_only_small_keys_and_only_into_chests(world):
    own, anywhere = Settings(), Settings(dungeon_items="anywhere")
    for item in (FOREST_KEY, FIRE_BOSS_KEY, FIRE_MAP, FIRE_COMPASS):
        assert is_restricted(world, own, item)
    assert not is_restricted(world, anywhere, FOREST_KEY)
    assert all(is_restricted(world, anywhere, item) for item in (FIRE_BOSS_KEY, FIRE_MAP, FIRE_COMPASS))
    assert not is_restricted(world, own, "Rupees (5)") and not is_restricted(world, anywhere, "Rupees (5)")

    assert not allowed(world, own, "Field Chest", FOREST_KEY)
    assert allowed(world, anywhere, "Field Chest", FOREST_KEY)
    assert allowed(world, anywhere, "Fire Key Chest", FOREST_KEY)  # another dungeon's chest is a chest too
    assert not allowed(world, anywhere, "Field Floor", FOREST_KEY)  # no named grant on a floor pick-up
    assert allowed(world, anywhere, "Forest Floor", FOREST_KEY)  # its own dungeon takes it anywhere, as before
    for item in (FIRE_BOSS_KEY, FIRE_MAP, FIRE_COMPASS):
        for settings in (own, anywhere):
            assert allowed(world, settings, "Fire Map Chest", item)
            assert not allowed(world, settings, "Field Chest", item)
            assert not allowed(world, settings, "Forest Key Chest", item)


def kit_world() -> dict:
    """A return kit (two small keys and the boss key of dungeon D among its families) placed in an adult phase,
    then dungeon stages, progression and filler; chests and floor pick-ups in and out of two keyed dungeons."""
    return {
        "start": "Root",
        "goal": "'D Clear'",
        "settings": {
            "starting_age": "child",
            "age_return_event": "D Clear",
            "age_return_region": "Field",
            "age_pull_event": "Time Travel",
            "age_return_guarantee": True,
            "age_return_fill_families": ["Strength", "Weapon", "Small Key (D)", "Boss Key (D)"],
            "age_return_bypass_families": ["Strength"],
            "age_return_fill_inventory": {"Song": 1, "Strength": 1},
        },
        "items": {
            "Song": {},
            "Strength": {},
            "Bracelet": {"alias": ["Strength", 1]},
            "Upgrade": {"alias": ["Strength", 2]},
            "Weapon": {},
            "Small Key (D)": {"type": "SmallKey"},
            "Boss Key (D)": {"type": "BossKey"},
            "Map (D)": {"type": "Map", "class": "priority"},
            "Small Key (E)": {"type": "SmallKey"},
            "Map (E)": {"type": "Map", "class": "priority"},
            "Rupee": {"class": "normal"},
        },
        "regions": [
            {"name": "Root", "exits": {"Field": "age == starting_age or 'Time Travel'"}},
            {
                "name": "Field",
                "events": {"Time Travel": "age == 'child' and Strength"},
                "locations": {
                    "Child Song": {"rule": "age == 'child'", "type": "NPC", "vanilla": "Song"},
                    "Child Bracelet": {"rule": "age == 'child' and Song", "type": "NPC", "vanilla": "Bracelet"},
                    "Shared A": check("Upgrade"),
                    "Shared B": check("Weapon"),
                    "Field Chest": check("Rupee"),
                    "Field Floor": check("Rupee", "Freestanding"),
                },
                "exits": {"Ledge": "age == 'adult'", "Cave": "True", "Dungeon": "age == 'adult'"},
            },
            {
                "name": "Ledge",
                "locations": {"Ledge Chest": check("Rupee"), "Ledge Floor": check("Rupee", "Freestanding")},
            },
            {
                "name": "Cave",
                "dungeon": "E",
                "locations": {"Cave Chest": check("Small Key (E)"), "Cave Floor": check("Map (E)", "Freestanding")},
                "exits": {"Cave Back": "Small_Key_E"},
            },
            {"name": "Cave Back", "dungeon": "E", "locations": {"Cave Back Chest": check("Rupee")}},
            {
                "name": "Dungeon",
                "dungeon": "D",
                "locations": {"First Key": check("Small Key (D)")},
                "exits": {"Middle": "Small_Key_D"},
            },
            {
                "name": "Middle",
                "dungeon": "D",
                "locations": {"Second Key": check("Small Key (D)"), "Middle Floor": check("Map (D)", "Freestanding")},
                "exits": {"End": "(Small_Key_D, 2)"},
            },
            {
                "name": "End",
                "dungeon": "D",
                "locations": {"Adult Chest": check("Rupee"), "Boss Chest": check("Boss Key (D)")},
                "exits": {"Boss Room": "Boss_Key_D"},
            },
            {"name": "Boss Room", "dungeon": "D", "events": {"D Clear": "Weapon and Song"}},
        ],
    }


def contract_breaks(seed: Seed) -> list[tuple[str, str]]:
    """Placements outside the contract: a dungeon item outside its dungeon unless a small key in a chest."""
    world, out = seed.world, []
    for name in seed.shuffled:
        item, loc = seed.placements[name], seed.world.locations[name]
        info = world.items[item]
        inside = info.dungeon is None or world.regions[loc.region].dungeon == info.dungeon
        if not inside and (info.type != SMALL_KEY or loc.type != "Chest"):
            out.append((name, item))
    return out


def test_every_stage_of_an_anywhere_fill_keeps_other_dungeon_items_home():
    settings = Settings(dungeon_items="anywhere", shuffle=("Chest", "Freestanding"))
    left = 0
    for number in range(30):
        seed = generate(kit_world(), number, settings)
        assert contract_breaks(seed) == [], number
        world = seed.world
        left += sum(
            world.items[item].type == SMALL_KEY and world.regions[world.locations[name].region].dungeon is None
            for name, item in seed.placements.items()
        )
        adult = Search.adult_after_pull(world, ["Song", "Bracelet"])
        adult.collect_spheres(seed.placements)
        assert adult.holds("D Clear"), number  # the return kit still works from the adult phase
    assert left > 0  # small keys do leave


@pytest.mark.parametrize(
    ("chest_kind", "event", "eligible"),
    [
        ("Obj_TBox_A_01_memo11", None, False),
        ("Obj_TBox_Unknown", None, False),
        ("Obj_TBox_A_01", None, True),
        ("Obj_TBox_A_01_NoBake", None, True),
        ("Obj_TBox_A_06", None, True),
        ("Obj_TBox_GlassTruth_A_01", None, True),
        ("Obj_TBox_A_02", None, True),
        ("Obj_TBox_A_03", None, True),
        ("Obj_TBox_A_01_memo11", "House_NaviChatOff", True),
    ],
)
def test_native_heart_piece_chest_requires_a_played_named_key_opening(chest_kind, event, eligible):
    spec = load_spec()
    world = build_world(spec)
    name = "Hyrule Field Chest (Obj_Heart_Piece)"
    chest = census_location(
        2967378296224661060,
        "HyruleField",
        ("Banc/HyruleField/Synthetic.bcett.byml.zs",),
        "Obj_Heart_Piece",
        event,
        gyaml=chest_kind,
    )
    links = Links({name: [chest]}, {chest.id: name}, [])
    native = build_world(restrict_key_openings(spec, world, links, EVENTS))
    settings = Settings(dungeon_items="anywhere")
    assert allowed(native, settings, name, FOREST_KEY) is eligible
    assert allowed(native, settings, name, "Rupees (5)")


def test_an_anywhere_seed_of_the_whole_world_keeps_the_contract():
    seed = generate(load_spec(), 0, Settings(dungeon_items="anywhere"))
    assert contract_breaks(seed) == []


# --------------------------------------------------------------------------------------------------------------
# The plan


def test_own_dungeon_plans_name_no_key_and_stay_as_before(world, links):
    plan = plan_for(
        world,
        links,
        "own_dungeon",
        {
            "Fire Key Chest": FOREST_KEY,  # the generic actor it already holds: left alone, as before
            "Field Chest": FIRE_KEY,
            "Spirit Hand Chest": SPIRIT_KEY,
            "Field Floor": FOREST_KEY,  # other kinds belong to their own patch steps, as before
            "Story Chest": FIRE_BOSS_KEY,
        },
    )
    assert rows(plan) == [
        ("Field Chest", FIELD_CHEST, (KF_ADULT, KF_CHILD), RUPEE, KEY_ACTOR, None),
        ("Story Chest", STORY_CHEST, (KF_ADULT, KF_CHILD), "Item_Sword", "Item_Dungeon_BossKey", None),
        ("Spirit Hand Chest", HAND_CHEST, (COLOSSUS,), RUPEE, KEY_ACTOR, None),
    ]
    assert ("Fire Key Chest", FIRE_KEY_CHEST) in plan.unchanged
    assert all("named_key" not in c and "key_event" not in c for c in plan.as_dict()["changes"])


def test_another_dungeons_key_in_a_key_chest_changes_while_its_own_stays(world, links):
    plan = plan_for(
        world,
        links,
        "anywhere",
        {"Fire Key Chest": FOREST_KEY, "Fire Map Chest": FIRE_KEY, "Forest Key Chest": FOREST_KEY},
    )
    assert rows(plan) == [
        ("Fire Key Chest", FIRE_KEY_CHEST, (FIRE,), KEY_ACTOR, KEY_ACTOR, "ForestTemple"),  # same actor, new target
        ("Fire Map Chest", FIRE_MAP_CHEST, (FIRE,), "Item_Dungeon_Map", KEY_ACTOR, None),  # its own: generic
    ]
    assert ("Forest Key Chest", FOREST_KEY_CHEST) in plan.unchanged
    assert plan.as_dict()["changes"][0]["named_key"] == "ForestTemple"


def test_two_targets_route_every_age_file_and_copy(world, links):
    plan = plan_for(world, links, "anywhere", {"Field Chest": FOREST_KEY, "Twin Chest": FIRE_KEY})
    assert rows(plan) == [
        ("Field Chest", FIELD_CHEST, (KF_ADULT, KF_CHILD), RUPEE, KEY_ACTOR, "ForestTemple"),
        ("Twin Chest", TWIN_CHILD, (KF_CHILD,), RUPEE, KEY_ACTOR, "FireTemple"),
        ("Twin Chest", TWIN_ADULT, (KF_ADULT,), RUPEE, KEY_ACTOR, "FireTemple"),
    ]
    assert plan.files() == [KF_ADULT, KF_CHILD]
    plan = bound(plan)
    for path in plan.files():
        tree = field_tree(path)
        patch_tree(tree, path, plan)
        twin = TWIN_CHILD if path == KF_CHILD else TWIN_ADULT
        expected = field_tree(path)
        for a in expected["Actors"]:
            if a["Hash"] in (FIELD_CHEST, twin):
                target = "ForestTemple" if a["Hash"] == FIELD_CHEST else "FireTemple"
                a["Dynamic"].update({"Drop__DropActor": KEY_ACTOR, "GetEventName": f"Bind_{target}"})
        assert byml.difference(tree, expected) is None, path


def test_source_event_classifications_survive_and_the_binding_lands_last(world, links):
    plan = plan_for(world, links, "anywhere", {"Kept Chest": FIRE_KEY, "Story Chest": FOREST_KEY})
    kept, story = plan.changes
    assert (kept.kept_event.name, kept.event, kept.named_key) == ("House_NaviChatOff", None, "FireTemple")
    assert (story.event.name, story.kept_event, story.named_key) == ("Story_GetSword", None, "ForestTemple")
    kept_row, story_row = plan.as_dict()["changes"]
    assert kept_row["kept_event"] == "House_NaviChatOff" and "key_event" not in kept_row
    assert story_row["removed_event"] == "Story_GetSword" and story_row["story_state"] == "nothing to restore"

    with pytest.raises(PatchError, match="has a key named FireTemple but no grant binding"):
        patch_tree(field_tree(KF_CHILD), KF_CHILD, plan)

    plan = bound(plan)
    assert plan.as_dict()["changes"][0]["key_event"] == "Bind_FireTemple"
    tree = field_tree(KF_CHILD)
    patch_tree(tree, KF_CHILD, plan)
    dynamic = {a["Hash"]: a.get("Dynamic") for a in tree["Actors"]}
    assert dynamic[KEPT_CHEST] == {"Drop__DropActor": KEY_ACTOR, "GetEventName": "Bind_FireTemple"}
    assert dynamic[STORY_CHEST] == {"Drop__DropActor": KEY_ACTOR, "GetEventName": "Bind_ForestTemple"}


def test_a_binding_chosen_for_another_event_state_is_refused(world, links):
    kept_plan = bound(plan_for(world, links, "anywhere", {"Kept Chest": FIRE_KEY}))
    tree = field_tree(KF_CHILD)
    actor_dynamic(tree, KEPT_CHEST)["GetEventName"] = "Other_Event"
    with pytest.raises(PatchError, match="its key binding 'Bind_FireTemple' was chosen for 'House_NaviChatOff'"):
        patch_tree(tree, KF_CHILD, kept_plan)

    plain_plan = bound(plan_for(world, links, "anywhere", {"Field Chest": FOREST_KEY}))
    tree = field_tree(KF_CHILD)
    actor_dynamic(tree, FIELD_CHEST)["GetEventName"] = "House_NaviChatOff"
    with pytest.raises(PatchError, match="was chosen for None"):
        patch_tree(tree, KF_CHILD, plain_plan)


def test_a_change_names_only_real_targets_and_binds_only_named_keys():
    base = ChestChange("Field Chest", FIELD_CHEST, "", (KF_CHILD,), "Obj_TBox_A_01", FOREST_KEY, RUPEE, KEY_ACTOR, None)
    assert replace(base, named_key="ForestTemple").key_event is None
    with pytest.raises(PatchError, match="'Forest Temple' is not a small-key target"):
        replace(base, named_key="Forest Temple")
    with pytest.raises(PatchError, match="needs a named key"):
        replace(base, key_event="Bind_ForestTemple")
    with pytest.raises(PatchError, match="must be an event name"):
        replace(base, named_key="ForestTemple", key_event="")


def test_the_spirit_hand_chest_is_named_by_the_banc_it_stands_in(world, links):
    anywhere = plan_for(world, links, "anywhere", {"Spirit Hand Chest": SPIRIT_KEY, "Spirit Hand Floor": "Sword"})
    assert rows(anywhere) == [("Spirit Hand Chest", HAND_CHEST, (COLOSSUS,), RUPEE, KEY_ACTOR, "SpiritTemple")]
    with pytest.raises(PatchError, match="Spirit Hand Floor: Small Key \\(Spirit Temple\\) outside its dungeon"):
        plan_for(world, links, "anywhere", {"Spirit Hand Floor": SPIRIT_KEY})


@pytest.mark.parametrize(
    ("moved", "message"),
    [
        ({"Field Floor": FOREST_KEY}, "Field Floor: .* needs a named grant, which only chests have"),
        ({"Field Chest": FIRE_BOSS_KEY}, "Field Chest: Boss Key .* outside Fire Temple, which has no named grant"),
        ({"Field Chest": FIRE_MAP}, "Field Chest: Map .* outside Fire Temple, which has no named grant"),
        ({"Fire Key Chest": FIRE_COMPASS, "Forest Key Chest": FIRE_COMPASS}, "Forest Key Chest: Compass"),
        ({"Field Chest": TEMPLE_KEY}, "Field Chest: Small Key \\(Temple\\) .* which has no small-key target"),
    ],
)
def test_anywhere_plans_refuse_dungeon_items_no_grant_can_credit(world, links, moved, message):
    with pytest.raises(PatchError, match=message):
        plan_for(world, links, "anywhere", moved)


def test_dungeon_items_inside_their_own_area_need_no_name(world, links):
    plan = plan_for(
        world,
        links,
        "anywhere",
        {"Forest Floor": FOREST_KEY, "Temple Chest": TEMPLE_KEY, "Fire Key Chest": FIRE_BOSS_KEY},
    )
    assert rows(plan) == [
        ("Fire Key Chest", FIRE_KEY_CHEST, (FIRE,), KEY_ACTOR, "Item_Dungeon_BossKey", None),
        ("Temple Chest", TEMPLE_CHEST, (TEMPLE,), RUPEE, KEY_ACTOR, None),
    ]


# --------------------------------------------------------------------------------------------------------------
# The writer


def actor(gyaml: str, actor_hash: int, dynamic: dict | None = None) -> dict:
    a = {"Gyaml": gyaml, "Hash": U64(actor_hash), "SRTHash": U32(actor_hash), "Translate": [F32(1.0)] * 3}
    if dynamic is not None:
        a["Dynamic"] = dynamic
    return a


def field_tree(path: str) -> dict:
    twin = TWIN_CHILD if path == KF_CHILD else TWIN_ADULT
    return {
        "Actors": [
            actor("Obj_TBox_A_01", FIELD_CHEST, {"Drop__DropActor": RUPEE}),
            actor("Obj_TBox_A_01", twin, {"Drop__DropActor": RUPEE}),
            actor("Obj_TBox_A_01", KEPT_CHEST, {"Drop__DropActor": RUPEE, "GetEventName": "House_NaviChatOff"}),
            actor("Obj_TBox_A_01", STORY_CHEST, {"Drop__DropActor": "Item_Sword", "GetEventName": "Story_GetSword"}),
            actor("Obj_Signboard", 7),
        ],
        "FilePath": path,
    }


def actor_dynamic(tree: dict, actor_hash: int) -> dict:
    return next(a for a in tree["Actors"] if a["Hash"] == actor_hash)["Dynamic"]


@pytest.fixture
def fake_romfs(tmp_path, zsdic_pack):
    root = tmp_path / "romfs"
    (root / "Pack").mkdir(parents=True)
    (root / zsdic.PACK_PATH).write_bytes(zsdic_pack)
    dicts = zsdic.Dictionaries.from_pack(zsdic_pack)
    table = rstb.ResourceSizeTable()
    for path in (KF_CHILD, KF_ADULT):
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(dicts.compress(path, byml.write(field_tree(path))))
        table.set(path, 1 << 20)
    (root / rstb.TABLE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / rstb.TABLE_PATH).write_bytes(dicts.compress(rstb.TABLE_PATH, rstb.write(table)))
    return root


def test_written_age_files_carry_each_binding_or_nothing_is_written(world, links, fake_romfs, tmp_path):
    plan = plan_for(world, links, "anywhere", {"Field Chest": FOREST_KEY, "Twin Chest": FIRE_KEY})
    with pytest.raises(PatchError, match="no grant binding"):
        write(plan, fake_romfs, tmp_path / "unbound")
    assert not (tmp_path / "unbound").exists()

    plan = bound(plan)
    written = write(plan, fake_romfs, tmp_path / "a")
    write(plan, fake_romfs, tmp_path / "b")
    assert [f.path for f in written] == [KF_ADULT, KF_CHILD]
    dicts = zsdic.Dictionaries.from_romfs(fake_romfs)
    for path in (KF_ADULT, KF_CHILD):
        data = (tmp_path / "a" / "romfs" / path).read_bytes()
        assert data == (tmp_path / "b" / "romfs" / path).read_bytes()  # deterministic
        tree = byml.read(dicts.decompress(path, data))
        expected = copy.deepcopy(field_tree(path))
        twin = TWIN_CHILD if path == KF_CHILD else TWIN_ADULT
        actor_dynamic(expected, FIELD_CHEST).update({"Drop__DropActor": KEY_ACTOR, "GetEventName": "Bind_ForestTemple"})
        actor_dynamic(expected, twin).update({"Drop__DropActor": KEY_ACTOR, "GetEventName": "Bind_FireTemple"})
        assert byml.difference(tree, expected) is None, path
