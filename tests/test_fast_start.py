"""Fast start (``clawshot.patch.gamedata``) on synthetic data: settings, the initial-value plan, the written files."""

import copy

import pytest

from clawshot.formats import byml, rstb, zsdic
from clawshot.formats.byml import I32, U32, U64
from clawshot.patch import gamedata
from clawshot.patch.gamedata import FastStartError, build, loads, plan_game_data, write
from clawshot.patch.plan import PatchError
from clawshot.save import murmur3_32

GDL = gamedata.GAME_DATA_LIST
LISTS = "Event/EventSetting/EventSettingComponentList"
INTRO_LIST = f"{LISTS}/Dm_Intro.engine__event__EventSettingComponentList.bgyml"
MOVIE_LIST = f"{LISTS}/Movie.engine__event__EventSettingComponentList.bgyml"
ROOMY = 1 << 20
STEPS = ["NotReady", "Ready", "Step01", "Complete"]


def h(name: str) -> U32:
    return U32(murmur3_32(name.encode()))


def flag(name, default, reset=8):
    return {"DefaultValue": default, "Hash": h(name), "ResetTypeValue": I32(reset), "SaveFileIndex": I32(0)}


def game_data_list() -> dict:
    return {
        "Data": {
            "Bool": [flag("Saw_Intro", False), flag("Door_Open", False), flag("Blocker", True), flag("Sys", False, 0)],
            "Int": [flag("Rupees", I32(0))],
            "Enum": [
                {
                    "DefaultValue": h("NotReady"),
                    "Hash": h("Step_Quest"),
                    "RawValues": STEPS,
                    "ResetTypeValue": I32(8),
                    "SaveFileIndex": I32(0),
                    "Values": [h(s) for s in STEPS],
                }
            ],
            "Bool64bitKey": [{"Hash": U64(1 << 40), "ResetTypeValue": I32(24), "SaveFileIndex": I32(0)}],
        },
        "MetaData": {"SaveTypeHash": U32(7)},
    }


def work(path: str) -> str:
    return "Work/" + path.removesuffix(".bgyml") + ".gyml"


EVENT_SETTINGS = [
    {"__RowId": "Dm_Intro", "EventSettingComponentList": work(INTRO_LIST)},
    {"__RowId": "Dm_Other", "EventSettingComponentList": work(MOVIE_LIST)},
]
INTRO = {
    "$parent": work(MOVIE_LIST),
    "Components": {"PlayEnv": "?Event/Env.bgyml", "SkipSetting": "?Event/DisableSkip.bgyml"},
}
MOVIE = {"Category": "TimelineEvent", "Components": {"ActorPos": "?Event/Pos.bgyml"}}

SETTINGS_TOML = """
[setting.intro]
default = true
skips = "the intro"
state = "nothing"
source = "synthetic"
skippable = ["Dm_Intro"]

[setting.door]
default = false
skips = "the door scene"
state = "door open"
source = "synthetic"
[setting.door.game_data]
Saw_Intro = true
Door_Open = true
Step_Quest = "Complete"

[setting.blocker]
default = false
skips = "the blocker"
state = "blocker gone"
source = "synthetic"
logic = "the path is open"
[setting.blocker.game_data]
Blocker = false
Door_Open = true
"""


@pytest.fixture
def settings():
    return loads(SETTINGS_TOML)


@pytest.fixture
def fake_romfs(tmp_path, zsdic_pack):
    root = tmp_path / "romfs"
    dicts = zsdic.Dictionaries.from_pack(zsdic_pack)
    files = {
        zsdic.PACK_PATH: zsdic_pack,
        GDL: dicts.compress(GDL, byml.write(game_data_list(), "big")),
        gamedata.EVENT_SETTING_TABLE: dicts.compress(gamedata.EVENT_SETTING_TABLE, byml.write(EVENT_SETTINGS)),
        INTRO_LIST: byml.write(INTRO),
        MOVIE_LIST: byml.write(MOVIE),
    }
    for path, content in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(content)
    write_size_table(root, dicts, {GDL: ROOMY, INTRO_LIST: ROOMY})
    return root


def write_size_table(root, dicts, entries):
    table = rstb.ResourceSizeTable()
    for path, size in entries.items():
        table.set(path, size)
    (root / rstb.TABLE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / rstb.TABLE_PATH).write_bytes(dicts.compress(rstb.TABLE_PATH, rstb.write(table)))


def test_the_game_default_is_the_intro_alone():
    assert gamedata.defaults(gamedata.load()) == ["intro"]


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ('[setting.a]\ndefault = true\nskips = "x"\nstate = "y"\nsource = "z"\nwhat = 1\nskippable = ["E"]', "unknown"),
        ('[setting.a]\ndefault = true\nskips = "x"\nstate = "y"\nskippable = ["E"]', "'source' is required"),
        ('[setting.a]\nskips = "x"\nstate = "y"\nsource = "z"\nskippable = ["E"]', "'default' is required"),
        ('[setting.a]\ndefault = true\nskips = "x"\nstate = "y"\nsource = "z"', "changes nothing"),
        (
            '[setting.a]\ndefault = true\nskips = "x"\nstate = "y"\nsource = "z"\n[setting.a.game_data]\nF = 1.5',
            "a value",
        ),
    ],
)
def test_settings_file_errors(text, message):
    with pytest.raises(FastStartError, match=message):
        loads(text)


def test_plan_resolves_names_and_enum_steps(settings):
    changes = plan_game_data(game_data_list(), gamedata.select(settings, ["door", "blocker"]))
    assert [(c.setting, c.name, c.type, c.old, c.new) for c in changes] == [
        ("door", "Saw_Intro", "Bool", False, True),
        ("door", "Door_Open", "Bool", False, True),
        ("door", "Step_Quest", "Enum", "NotReady", "Complete"),
        ("blocker", "Blocker", "Bool", True, False),
    ]  # Door_Open is set by both settings to the same value: one change


def one_setting(game_data: str) -> gamedata.FastStartSetting:
    text = f'[setting.a]\ndefault = false\nskips = "x"\nstate = "y"\nsource = "z"\n[setting.a.game_data]\n{game_data}'
    return loads(text)["a"]


@pytest.mark.parametrize(
    ("game_data", "message"),
    [
        ("Nope = true", "no entry named 'Nope'"),
        ("Saw_Intro = 1", "is a Bool; its value must be bool"),
        ("Rupees = true", "is a Int; its value must be int"),
        ('Step_Quest = "Step02"', "'Step02' is not one of"),
        ("Step_Quest = true", "is a Enum"),
        ("Blocker = true", "is already True"),
        ("Sys = true", "is not reset on New Game"),
    ],
)
def test_plan_refuses_values_the_game_data_cannot_take(game_data, message):
    with pytest.raises(FastStartError, match=message):
        plan_game_data(game_data_list(), [one_setting(game_data)])


def test_plan_refuses_two_settings_that_disagree(settings):
    with pytest.raises(FastStartError, match="Step_Quest: 'door' sets it to 'Complete'"):
        plan_game_data(game_data_list(), [settings["door"], one_setting('Step_Quest = "Step01"')])


def test_write_changes_only_the_chosen_initial_values_and_the_skip_setting(fake_romfs, tmp_path, settings):
    before = {p: p.read_bytes() for p in fake_romfs.rglob("*") if p.is_file()}
    out = tmp_path / "out"
    written = write(fake_romfs, out, ["intro", "door", "blocker"], settings)

    assert [f.path for f in written] == [GDL, INTRO_LIST]
    assert sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()) == [
        f"romfs/{INTRO_LIST}",
        f"romfs/{GDL}",
    ]
    dicts = zsdic.Dictionaries.from_romfs(fake_romfs)
    data = dicts.decompress(GDL, (out / "romfs" / GDL).read_bytes())
    assert byml.byte_order(data) == "big"  # written in the order it was read
    expected = game_data_list()
    bools = {e["Hash"]: e for e in expected["Data"]["Bool"]}
    bools[h("Saw_Intro")]["DefaultValue"] = True
    bools[h("Door_Open")]["DefaultValue"] = True
    bools[h("Blocker")]["DefaultValue"] = False
    expected["Data"]["Enum"][0]["DefaultValue"] = h("Complete")  # the enum keeps its U32 node type
    assert byml.difference(byml.read(data), expected) is None
    assert len(data) == written[0].size == written[0].new_size

    intro = byml.read((out / "romfs" / INTRO_LIST).read_bytes())
    assert byml.difference(intro, {**INTRO, "Components": {"PlayEnv": "?Event/Env.bgyml"}}) is None
    assert {p: p.read_bytes() for p in fake_romfs.rglob("*") if p.is_file()} == before


def test_a_setting_without_game_data_leaves_game_data_list_alone(fake_romfs, settings):
    assert [f.path for f in build(fake_romfs, ["intro"], settings)] == [INTRO_LIST]


def test_unknown_setting_names_are_refused(fake_romfs, settings):
    with pytest.raises(FastStartError, match=r"unknown fast-start settings \['outro'\]"):
        build(fake_romfs, ["intro", "outro"], settings)


def test_skippable_refuses_a_shared_list_a_parent_skip_and_an_event_already_skippable(fake_romfs, settings):
    dicts = zsdic.Dictionaries.from_romfs(fake_romfs)
    table = fake_romfs / gamedata.EVENT_SETTING_TABLE

    shared = [*EVENT_SETTINGS, {"__RowId": "Dm_Twin", "EventSettingComponentList": work(INTRO_LIST)}]
    table.write_bytes(dicts.compress(gamedata.EVENT_SETTING_TABLE, byml.write(shared)))
    with pytest.raises(FastStartError, match=r"shared with \['Dm_Twin'\]"):
        build(fake_romfs, ["intro"], settings)

    table.write_bytes(dicts.compress(gamedata.EVENT_SETTING_TABLE, byml.write(EVENT_SETTINGS)))
    movie = copy.deepcopy(MOVIE)
    movie["Components"]["SkipSetting"] = "?Event/DisableSkip.bgyml"
    (fake_romfs / MOVIE_LIST).write_bytes(byml.write(movie))
    with pytest.raises(FastStartError, match="parent list .*Movie.* sets a SkipSetting too"):
        build(fake_romfs, ["intro"], settings)

    (fake_romfs / MOVIE_LIST).write_bytes(byml.write(MOVIE))
    (fake_romfs / INTRO_LIST).write_bytes(byml.write({**INTRO, "Components": {"PlayEnv": "?Event/Env.bgyml"}}))
    with pytest.raises(FastStartError, match="skippable already"):
        build(fake_romfs, ["intro"], settings)


def test_nothing_is_written_when_a_file_outgrows_its_size_table_entry(fake_romfs, tmp_path, settings, zsdic_pack):
    write_size_table(fake_romfs, zsdic.Dictionaries.from_pack(zsdic_pack), {GDL: ROOMY, INTRO_LIST: 16})
    out = tmp_path / "out"
    with pytest.raises(FastStartError, match="do not fit its size-table entry 16"):
        write(fake_romfs, out, ["door", "intro"], settings)
    assert not out.exists()


def test_write_needs_an_empty_folder_outside_the_romfs(fake_romfs, tmp_path, settings):
    with pytest.raises(PatchError, match="overlaps the romfs"):
        write(fake_romfs, fake_romfs / "out", ["intro"], settings)
    (tmp_path / "used").mkdir()
    (tmp_path / "used" / "x").write_text("x")
    with pytest.raises(PatchError, match="not empty"):
        write(fake_romfs, tmp_path / "used", ["intro"], settings)


def test_the_dpad_is_always_there_and_not_a_choice():
    always = {setting.name: setting for setting in gamedata.load_always()}
    assert always["dpad"].game_data == {"ActionGuide_IsEnd.Navi": True}
    assert "dpad" not in gamedata.load()  # never offered as a fast-start choice
