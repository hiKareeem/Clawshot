"""Every inventoried flowchart and timeline prop shows the given item through its container, against the dump (spec
event-items 2.2, 2.3, 2.6; plan 9.1, 9.5)."""

from pathlib import Path

import pytest

from clawshot.census.gifts import FLOW_VERSIONS, flow_files
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import evfl, zsdic
from clawshot.generate.rewards import catalog
from clawshot.patch import containers, event_models, event_props
from clawshot.patch.event_props import PLACEMENT

pytestmark = pytest.mark.dump

GIVEN = "Item_Boomerang"
REWARD = "Item_Medal_Shadow"


def _moved() -> dict[str, str]:
    slots = catalog()["slots"]
    return {p.check: (REWARD if p.check in slots else GIVEN) for p in event_props.load().props}


def test_dump_every_prop_of_a_moved_check_names_its_container_and_nothing_else_is_renamed(romfs):
    moved = _moved()
    transforms, packs = event_models.seed_changes(romfs, moved)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(Path(romfs), dicts, FLOW_VERSIONS)["Versions"].items()}
    files = flow_files(Path(romfs), versions)
    props = [p for p in event_props.load().props if p.part != PLACEMENT]
    for event in sorted({p.event for p in props}):
        path = files[event]
        data = dicts.decompress(path, (romfs / path).read_bytes())
        before, after = evfl.read(data), evfl.read(transforms[path](data))
        chart_before = before.flowchart or before.timeline
        chart_after = after.flowchart or after.timeline
        mine = {(p.actor, p.secondary): containers.container_name(moved[p.check]) for p in props if p.event == event}
        for old, new in zip(chart_before.actors, chart_after.actors, strict=True):
            expected = mine.get((old.name, old.secondary_name), old.name)
            assert new.name == expected, (event, old.name, new.name)
            assert (new.secondary_name, new.actions, new.params) == (old.secondary_name, old.actions, old.params)
        if after.flowchart is not None:
            assert after.flowchart.events == before.flowchart.events, event
        else:
            assert after.timeline.clips == before.timeline.clips, event
    assert sorted(packs) == [f"Pack/Actor/{containers.container_name(m)}.pack.zs" for m in sorted({GIVEN, REWARD})]


def test_dump_every_boss_reward_scene_has_a_prop_for_its_slot():
    slots = catalog()["slots"]
    with_props = {p.check for p in event_props.load().props}
    assert sorted(set(slots) - with_props) == []


def test_dump_a_moved_moat_check_changes_the_moat_pack_and_chains_the_row_edits_with_the_containers(romfs):
    from clawshot.formats import byml, sarc
    from clawshot.patch import placed_models
    from clawshot.patch.actor_packs import actor_member

    moat = next(p for p in event_props.load().props if p.part == PLACEMENT and p.check == "HF Ocarina of Time Item")
    transforms, packs = event_models.seed_changes(romfs, {moat.check: "Obj_Heart_Piece"})
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    path = f"Pack/Actor/{moat.actor}.pack.zs"
    data = dicts.decompress(path, (romfs / path).read_bytes())
    out = sarc.read(transforms[path](data))
    components = byml.read(out[actor_member(moat.actor)])["Components"]
    assert components["ModelInfoRef"] == "?" + placed_models.member_name(moat.actor)
    assert byml.read(out[placed_models.member_name(moat.actor)])["FmdbName"] == "Obj_Heart_Piece"
    assert set(placed_models.added_member_sizes(data, transforms[path](data))) == {
        placed_models.member_name(moat.actor)
    }
    table = containers.ACTOR_INFO
    rows = {
        r["__RowId"]: r for r in byml.read(transforms[table](dicts.decompress(table, (romfs / table).read_bytes())))
    }
    assert rows[moat.actor]["FmdbName"] == "Obj_Heart_Piece"  # the moat row
    assert rows[containers.container_name("Obj_Heart_Piece")]["FmdbName"] == "Obj_Heart_Piece"  # and the containers'
    assert sorted(packs) == ["Pack/Actor/Dm_Item_Clawshot_Obj_Heart_Piece.pack.zs"]


RUTO_STONE = "Obj_InsideJabu_Jabu_Stone_Water_A_01"


def test_dump_rutos_stone_shows_barinades_reward_through_its_own_model_member(romfs):
    """Plan 10b.1 (decision Q6): with Barinade's reward moved, the stone Ruto shows in Jabu-Jabu keeps its actor and
    shows the reward's model through a uniquely named ModelInfo member; its row shows the model too."""
    from clawshot.formats import byml, sarc
    from clawshot.patch import getitem, placed_models
    from clawshot.patch.actor_packs import actor_member

    transforms, _ = event_models.seed_changes(romfs, {"Barinade": REWARD})
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    path = f"Pack/Actor/{RUTO_STONE}.pack.zs"
    assert path in transforms
    data = dicts.decompress(path, (romfs / path).read_bytes())
    changed = transforms[path](data)
    out = sarc.read(changed)
    components = byml.read(out[actor_member(RUTO_STONE)])["Components"]
    assert components["ModelInfoRef"] == "?" + placed_models.member_name(RUTO_STONE)
    model = getitem.model_actor(REWARD)
    assert byml.read(out[placed_models.member_name(RUTO_STONE)])["FmdbName"] == model
    assert set(placed_models.added_member_sizes(data, changed)) == {placed_models.member_name(RUTO_STONE)}
    assert sarc.read(sarc.write(out)) == out  # the rewritten pack round-trips (10b.4)
    table = containers.ACTOR_INFO
    rows = {
        r["__RowId"]: r for r in byml.read(transforms[table](dicts.decompress(table, (romfs / table).read_bytes())))
    }
    assert rows[RUTO_STONE]["FmdbName"] == model


def test_dump_rutos_stone_is_untouched_when_barinade_keeps_his_stone_or_nothing_moved(romfs):
    """Plan 10b.2: Barinade vanilla (not in ``moved``) leaves the stone's pack and rows alone."""
    path = f"Pack/Actor/{RUTO_STONE}.pack.zs"
    transforms, _ = event_models.seed_changes(romfs, {"HF Ocarina of Time Item": "Obj_Heart_Piece"})
    assert path not in transforms
    assert event_models.seed_changes(romfs, {}) == ({}, {})


def test_dump_rutos_stone_takes_every_reward_barinade_can_hold(romfs):
    """Plan 10b.1: dungeon reward shuffle puts any stone or medallion at Barinade; each one's model must fit the stone
    (no refused AnimationRef, the pack reads back)."""
    from clawshot.formats import sarc

    dicts = zsdic.Dictionaries.from_romfs(romfs)
    path = f"Pack/Actor/{RUTO_STONE}.pack.zs"
    data = dicts.decompress(path, (romfs / path).read_bytes())
    rewards = sorted({slot["actor"] for slot in catalog()["slots"].values()} - {"Item_Stone_Water"})
    assert len(rewards) == 8
    for reward in rewards:
        transforms, _ = event_models.seed_changes(romfs, {"Barinade": reward})
        assert sarc.read(transforms[path](data)), reward


def test_dump_links_hand_in_the_moat_scene_takes_the_given_items_container(romfs):
    """Played run E10, pilot arm A (BBender 2026-11-26): with the moat check moved, the real Dm_MelodyGet_Time gets the
    container bound to Link's left hand before C01 and sent offstage before C05; Zelda's ocarina keeps its name."""
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dicts, FLOW_VERSIONS)["Versions"].items()}
    path = flow_files(romfs, versions)["Dm_MelodyGet_Time"]
    transforms, packs = event_models.seed_changes(romfs, {"HF Ocarina of Time Item": "Obj_Heart_Piece"})
    chart = evfl.read(transforms[path](dicts.decompress(path, (romfs / path).read_bytes()))).flowchart
    container = containers.container_name("Obj_Heart_Piece")
    hands = [i for i, a in enumerate(chart.actors) if (a.name, a.secondary_name) == (container, "hand")]
    assert len(hands) == 1
    bind = chart.events[chart.entry_point("C01").main_event]
    assert (
        bind.actor == hands[0] and bind.params["ActorName"] == "Player_Event" and bind.params["BoneName"] == "Weapon_L"
    )
    off = chart.events[chart.entry_point("C05").main_event]
    assert off.actor == hands[0] and chart.actors[off.actor].actions[off.action] == "EventGoOffstageForUser"
    assert [a.name for a in chart.actors].count("Dm_Item_Ocarina_Time") == 1  # Zelda's ocarina, played: unchanged
    assert f"Pack/Actor/{container}.pack.zs" in packs


def test_dump_links_hand_holds_a_piece_of_heart_by_its_middle(romfs):
    """D19 (BBender, 2026-11-26, played run S6): the hand bind's TransOffset is the native ocarina's box centre minus
    the heart's, as f32; the value the played pilot wrote (tools/build_hand_offset_pilot.py)."""
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dicts, FLOW_VERSIONS)["Versions"].items()}
    path = flow_files(romfs, versions)["Dm_MelodyGet_Time"]
    transforms, _ = event_models.seed_changes(romfs, {"HF Ocarina of Time Item": "Obj_Heart_Piece"})
    chart = evfl.read(transforms[path](dicts.decompress(path, (romfs / path).read_bytes()))).flowchart
    bind = next(event for event in chart.events if event.name == "Clawshot_hand_bind")
    assert list(bind.params["TransOffset"]) == [-0.0087890625, -0.17549985647201538, 0.0017242431640625]
    zelda = next(i for i, a in enumerate(chart.actors) if a.name == "Dm_Item_Ocarina_Time")
    native = [
        e for e in chart.events if isinstance(e, evfl.ActionEvent) and e.actor == zelda and "TransOffset" in e.params
    ]
    assert native and all(e.params["TransOffset"] == (0.0, 0.0, 0.0) for e in native)  # the scene's own binds (D6)


def test_dump_the_shared_get_subflow_names_zeldas_letter_container_when_her_letter_moves(romfs):
    """Played run r1-zelda2 (BBender, 2026-11-26): Dm_SY_GetInEvent's own Item_ZeldaLetter (sent offstage for the get
    pose, Event335) must be the same actor as the scene's prop, so it takes the same container; nothing else in it
    changes, and it stays native when the letter does not move."""
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dicts, FLOW_VERSIONS)["Versions"].items()}
    path = flow_files(romfs, versions)["Dm_SY_GetInEvent"]
    native = evfl.read(dicts.decompress(path, (romfs / path).read_bytes())).flowchart
    transforms, _ = event_models.seed_changes(romfs, {"HC Zeldas Letter": "Obj_Heart_Piece"})
    chart = evfl.read(transforms[path](dicts.decompress(path, (romfs / path).read_bytes()))).flowchart
    container = containers.container_name("Obj_Heart_Piece")
    names = [a.name for a in chart.actors]
    assert names == [container if a.name == "Item_ZeldaLetter" else a.name for a in native.actors]
    assert container in names and "Item_ZeldaLetter" not in names
    unmoved, _ = event_models.seed_changes(romfs, {"LW Gift from Saria": "Obj_Heart_Piece"})
    assert path not in unmoved


# ---------------------------------------------------------------------------------------------------------------
# D20 (pilot A, BBender, runs S12, S13): the scene animations a flow plays on a song container start its effect.


def _flows(romfs: Path):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dicts, FLOW_VERSIONS)["Versions"].items()}
    files = flow_files(romfs, versions)

    def read(event: str) -> evfl.EventFlowFile | None:
        return (
            evfl.read(dicts.decompress(files[event], (romfs / files[event]).read_bytes())) if event in files else None
        )

    return dicts, read


def _played(chart: evfl.Flowchart, actor: str, secondary: str) -> set[str]:
    found = {i for i, a in enumerate(chart.actors) if (a.name, a.secondary_name) == (actor, secondary)}
    return {
        e.params["ASName"]
        for e in chart.events
        if isinstance(e, evfl.ActionEvent)
        and e.actor in found
        and chart.actors[e.actor].actions[e.action] == event_models.PLAY_AS
    }


def test_dump_every_animation_a_flowchart_prop_plays_is_one_its_song_event_user_can_answer(romfs):
    """A prop with ``scene_as``: its set is one its EventSetting row loads, and that set's ASB holds every node the
    flow plays on the prop. A prop without: it plays only nodes the effect donor's user (copied by every song event
    user) answers already (Light Arrows' Rotate_GetDemo). A subflow its event calls plays nothing on the prop."""
    from clawshot.census.gifts import EVENT_SETTING
    from clawshot.formats import elink
    from clawshot.patch import songs

    dicts, read = _flows(romfs)
    settings = {row["__RowId"]: row for row in read_romfs_byml(romfs, dicts, EVENT_SETTING)}
    table = elink.decode(dicts.decompress(songs.ELINK, (romfs / songs.ELINK).read_bytes()))
    donor = {action for _, action, _ in table.action_triggers(songs.EFFECT_DONOR)}
    checked = 0
    for prop in event_props.load().props:
        if prop.part != "flowchart":
            continue
        chart = read(prop.event).flowchart
        played = _played(chart, prop.actor, prop.secondary)
        if prop.scene_as:
            sets = (settings[prop.event].get("ExtraResources") or {}).get("EventAS") or []
            assert f"Work/AS/Root/Event/{prop.scene_as}.root.as" in sets, prop.id
            path = f"AS/{prop.scene_as}.root.asb.zs"
            asb = dicts.decompress(path, (romfs / path).read_bytes())
            assert played and all(b"\0" + n.encode() + b"\0" in asb for n in played), (prop.id, played)
            assert event_models.scene_actions(read(prop.event), prop) == sorted(f"{prop.scene_as}/{n}" for n in played)
            checked += 1
        else:
            assert played <= donor, (prop.id, played - donor)
        called = {e.flowchart for e in chart.events if getattr(e, "flowchart", "") not in ("", prop.event, None)}
        for name in sorted(called):
            sub = read(name)
            if sub is not None and sub.flowchart is not None:
                assert not _played(sub.flowchart, prop.actor, prop.secondary), (prop.id, name)
    assert checked >= 3  # the target's two bags and Darunia's gauntlet at least


def test_dump_every_song_event_user_answers_the_scene_animations_its_seed_plays_on_song_containers(romfs):
    """With songs at the target, Darunia, Zelda's Letter and Saria: every song event user has a trigger per scene
    animation played on those containers, each starting GetDemo as Rotate_GetDemo does; every native user is
    byte-identical; Saria's farewell adds none (it plays no scene animation on the prop)."""
    from clawshot.formats import elink
    from clawshot.patch import songs

    moved = {
        "LW Target in Woods": "Item_Melody_EponaSong",
        "GC Darunias Joy": "Item_Melody_StormSong",
        "HC Zeldas Letter": "Item_Melody_FireBolero",
        "LW Gift from Saria": "Item_Melody_ZeldaLullaby",
    }
    dicts, read = _flows(romfs)
    props = [p for p in event_props.load().props if p.check in moved and p.part == "flowchart"]
    expected = sorted(
        {
            f"{p.scene_as}/{n}"
            for p in props
            if p.scene_as
            for n in _played(read(p.event).flowchart, p.actor, p.secondary)
        }
    )
    assert "Dm_Goron_0030_Gauntlet_Goron/C09-Gauntlet" in expected
    assert "Dm_LostWood_0040_Item_BulletBag_Large/C02" in expected
    assert "Dm_LostWood_0040_Item_BulletBag_Medium/C02" in expected
    transforms, _ = event_models.seed_changes(romfs, moved)
    native_bytes = dicts.decompress(songs.ELINK, (romfs / songs.ELINK).read_bytes())
    native, table = elink.decode(native_bytes), elink.decode(transforms[songs.ELINK](native_bytes))
    after = dict(table.users)
    for key, data in native.users:  # by name hash: some native names are not in the name table
        assert after[key] == data, f"{key:08x}"
    heart = native.action_triggers(songs.EFFECT_DONOR)
    for song in moved.values():
        user = songs.event_user_name(song)
        triggers = table.action_triggers(user)
        scenes = [(action, keys) for slot, action, keys in triggers if slot == songs.SCENE_SLOT and "/" in action]
        assert scenes == [(action, ["GetDemo"]) for action in sorted(expected, key=lambda a: a.lower())], user
        assert [t for t in triggers if "/" not in t[1]] == heart, user  # the donor's own triggers stay
