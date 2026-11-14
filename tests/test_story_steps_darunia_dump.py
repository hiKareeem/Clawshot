"""Combined D/E source-once behavior through a real full-world seed and written native flows.

The interpreter exercises saved-state transitions and registered subflows, not engine timing or animation.
Late NPC availability and actual save persistence still require the staged Longshot check.
"""

import pytest
from test_story_steps_darunia import BRACELET, BRACELET_OWNED, OPENED, STEP, STEPS, play
from test_story_steps_fire import DOOR_FLOW, ROOM, SOURCES

from clawshot.census.hints import flow_path
from clawshot.formats import byml, evfl, zsdic
from clawshot.generate import Settings
from clawshot.patch import darunia, make_seed, write_seed
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.save import key

pytestmark = pytest.mark.dump

CHECK = "GC Darunias Joy"
POUCH = "Event/EventFlow/GetPouchContent.bfevfl.zs"
BASE_PATHS = (darunia.STONE_FLOW, darunia.MOVIE_FLOW, POUCH)
PATCHED_PATHS = (*BASE_PATHS, DOOR_FLOW)
MEADOW_FLOW = "Event/EventFlow/SacredForestMeadow.bfevfl.zs"
SONG_FLOW = "Event/EventFlow/Dm_MelodyGet_Saria.bfevfl.zs"
PATHS = (*PATCHED_PATHS, MEADOW_FLOW, SONG_FLOW)
PHASES = ("SariaMelodyPlay", "DodongoCavernOpne", "DungeonStart", "BossBattle", "EscapeDungeon", "Complete")


@pytest.fixture(scope="module")
def produced(romfs, tmp_path_factory):
    """Full production world: a slice would exclude Darunia from D's native-bonus source scan."""
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    native = {path: dictionaries.decompress(path, (romfs / path).read_bytes()) for path in PATHS}
    output = make_seed(romfs, 7, Settings())
    assert output.seed.world.progressive_copies_only
    assert CHECK not in output.seed.shuffled
    destination = tmp_path_factory.mktemp("darunia-combined")
    write_seed(output, romfs, destination)
    for path in PATCHED_PATHS:
        assert (destination / "romfs" / path).is_file(), path
    # Resolve the same sparse mod overlay as the runtime: untouched song presentation stays native.
    written = {}
    for path in PATHS:
        override = destination / "romfs" / path
        source = override if override.is_file() else romfs / path
        written[path] = dictionaries.decompress(path, source.read_bytes())
    for path, data in written.items():
        assert evfl.write(evfl.read(data)) == data, path
    return native, written


def documents(flows):
    return tuple(evfl.read(flows[path]) for path in BASE_PATHS)


def test_the_source_flag_is_saved_and_uncollected_on_new_game(romfs):
    assert flow_path(romfs, "Get_StoneOfFire") == darunia.STONE_FLOW
    assert flow_path(romfs, "Dm_Goron_0030") == darunia.MOVIE_FLOW
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    data = byml.read(dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes()))["Data"]
    source = {int(row["Hash"]): row for row in data["Bool"]}[key(darunia.SOURCE)]
    assert (source["DefaultValue"], int(source["ResetTypeValue"]), int(source["SaveFileIndex"])) == (False, 8, 0)
    # The interpreter compares ordinal steps, not their numerically unordered saved hashes.
    fire = {int(row["Hash"]): row for row in data["Enum"]}[key(STEP)]
    assert tuple(fire["RawValues"]) == STEPS
    assert [int(value) for value in fire["Values"]] == [key(step) for step in STEPS]
    expressions = {int(row["Hash"]): row for row in data["BoolExp"]}
    for _, _, target in SOURCES:
        expression = expressions[key(f"Get_StoneOfFire_IsAfter_{target}_Exp")]
        assert [[int(value) for value in term] for term in expression["Values"]] == [
            [12, key(STEP)],  # native enum-read operand
            [2, key(target)],  # native strict-greater operand
        ]


@pytest.mark.parametrize("step", PHASES)
@pytest.mark.parametrize(
    "owned,grants_child_item",
    [
        pytest.param((), True, id="child-item-missing"),
        pytest.param((BRACELET_OWNED,), False, id="child-item-already-owned"),
        pytest.param(
            ("Armor_Adult_Gauntlet_Silver", "Armor_Adult_Gauntlet_Gold"),
            True,
            id="adult-items-do-not-replace-child-item",
        ),
    ],
)
def test_combined_native_paths_collect_once_without_regressing_fire(produced, step, owned, grants_child_item):
    native, written = produced
    stone, movie, pouch = documents(written)
    after, result = play(stone, movie, pouch=pouch, step=step, owned=owned)
    assert result["rewards"] == ([BRACELET] if grants_child_item else [])
    assert after[darunia.SOURCE] is True
    assert result["writes"] == ([(step, "DodongoCavernOpne")] if STEPS.index(step) < OPENED else [])
    assert STEPS.index(after[STEP]) >= STEPS.index(step)

    # Crucial D/E composition: its real lower-tier skip still returns to E's source flag.
    assert any(name.startswith("Clawshot_Bonus_Dm_Goron_0030_Event127") for name in result["trace"])
    assert "Event149" in result["trace"]  # native camera-reset tail continues after either guard branch
    _, repeat = play(stone, movie, pouch=pouch, step=after[STEP], source=True, owned=owned)
    assert repeat["rewards"] == [] and repeat["writes"] == []

    if STEPS.index(step) >= OPENED:
        old_stone, old_movie, _ = documents(native)
        _, original = play(old_stone, old_movie, step=step, owned=owned)
        assert original["rewards"] == []  # the native missable source, before E's fix


@pytest.mark.parametrize("step", ["SariaMelodyPlay", "DungeonStart"])
def test_wrong_song_still_cannot_collect_the_combined_source(produced, step):
    _, written = produced
    stone, movie, pouch = documents(written)
    after, result = play(stone, movie, pouch=pouch, step=step, song=False)
    assert result["rewards"] == [] and result["writes"] == []
    assert after[STEP] == step and after[darunia.SOURCE] is False


@pytest.mark.parametrize("step", ["DungeonStart", "Complete"])
def test_native_boulder_then_room_door_meeting_and_dance_preserves_progress(produced, step):
    _, written = produced
    stone, movie, pouch = documents(written)
    after, result = play(
        stone,
        movie,
        pouch=pouch,
        step=step,
        owned=(BRACELET_OWNED,),
        entries=(
            ("Get_StoneOfFire", "GoronCity_PlayZeldasLullaby"),
            ("Get_StoneOfFire", ROOM),
            ("Get_StoneOfFire", "Get_StoneOfFire_PlayOcarina"),
        ),
    )
    assert after[STEP] == step
    assert after["IsZeldaLullabyPlayed_DaruniaEntrance"] is True
    assert after[darunia.SOURCE] is True
    assert result["writes"] == []
    assert result["rewards"] == []  # the owned child Bracelet is not another strength upgrade


@pytest.mark.parametrize("flow,entry,target", SOURCES)
@pytest.mark.parametrize("boundary", ["before", "equal", "after", "complete"])
def test_native_source_boundaries_and_natural_order(produced, flow, entry, target, boundary):
    native, written = produced
    index = STEPS.index(target)
    step = STEPS[
        {"before": index - 1, "equal": index, "after": index + 1, "complete": STEPS.index("Complete")}[boundary]
    ]
    stone, movie, pouch = documents(written)
    after, result = play(
        stone,
        movie,
        pouch=pouch,
        step=step,
        extra=(evfl.read(written[DOOR_FLOW]),),
        entries=((flow, entry),),
    )
    assert after[STEP] == (target if STEPS.index(step) <= index else step)
    assert result["writes"] == ([(step, target)] if STEPS.index(step) <= index else [])
    if flow == "DoorOfTime":
        assert after["Step_DoorOfTime"] == "Step02"  # Zelda/Impa's own continuation still runs
    if STEPS.index(step) <= index:
        old_stone, old_movie, old_pouch = documents(native)
        expected, old = play(
            old_stone,
            old_movie,
            pouch=old_pouch,
            step=step,
            extra=(evfl.read(native[DOOR_FLOW]),),
            entries=((flow, entry),),
        )
        assert after == expected
        assert (result["rewards"], result["writes"], result["notices"]) == (
            old["rewards"],
            old["writes"],
            old["notices"],
        )


@pytest.mark.parametrize("step", ["SariaMelodyGet", "Complete"])
def test_native_meadow_lesson_grants_song_without_losing_later_fire_progress(produced, step):
    _, written = produced
    stone, movie, pouch = documents(written)
    after, result = play(
        stone,
        movie,
        pouch=pouch,
        step=step,
        extra=(evfl.read(written[MEADOW_FLOW]), evfl.read(written[SONG_FLOW])),
        entries=(("SacredForestMeadow", "SacredForestMeadow_Field_MelodyGet_Saria"),),
    )
    assert after["IsGet.Item_Melody_SariaSong"] is True
    assert result["rewards"] == ["Item_Melody_SariaSong"]
    assert after[STEP] == ("SariaMelodyPlay" if step == "SariaMelodyGet" else "Complete")
    assert result["writes"] == ([("SariaMelodyGet", "SariaMelodyPlay")] if step == "SariaMelodyGet" else [])
