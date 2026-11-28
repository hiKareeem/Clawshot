"""Container actors: one model-only event prop per model a seed needs (spec event-items 2.4, D14-D16; plan task 7)."""

import pytest

from clawshot.formats import byml, sarc
from clawshot.patch import containers, getitem, songs
from clawshot.patch import custom_items as custom
from clawshot.patch.actor_packs import actor_member, closure
from clawshot.patch.plan import PatchError

DONOR = containers.DONOR
DONOR_PARAM = actor_member(DONOR)
DONOR_INFO = "Component/ModelInfo/Item_Ocarina_Fairy.engine__component__ModelInfo.bgyml"
DUMMY_ANIM = "Component/AnimationParam/Dummy.engine__component__AnimationParam.bgyml"
DONOR_ELINK = "Component/ELink/Item_Ocarina_Fairy.engine__component__ELinkParam.bgyml"
BIND = "Component/ModelBindParam/Item_Ocarina_Fairy.engine__component__ModelBindParam.bgyml"
PERFORMER = "Component/EventPerformerParam/Common.engine__component__EventPerformerParam.bgyml"


def donor_pack() -> dict[str, bytes]:
    components = {
        "ASRef": "?AS/DemoDummy.root.asb",
        "ActorLogicNodeRef": "Work/Logic/NodeDefinition/Node/ActorLogicSimpleActor.aidefn",
        "AnimationRef": "?" + DUMMY_ANIM,
        "ELinkRef": "?" + DONOR_ELINK,
        "EventPerformerRef": "?" + PERFORMER,
        "ModelBindRef": "?" + BIND,
        "ModelInfoRef": "?" + DONOR_INFO,
    }
    return {
        DONOR_PARAM: byml.write({"Components": components}),
        DONOR_INFO: byml.write({"FmdbName": "Item_Ocarina_Fairy", "ModelProjectName": "Item_Ocarina_Fairy"}),
        DUMMY_ANIM: byml.write({"AnimationResources": []}),
        DONOR_ELINK: byml.write({"UserName": "Item_Ocarina_Fairy"}),
        BIND: byml.write({}),
        PERFORMER: byml.write({"UseEventUniqueAin": True}),
    }


SWORD = "Item_Sword_Biggoron"
SWORD_INFO = "Component/ModelInfo/Weapon_Sword_Biggoron.engine__component__ModelInfo.bgyml"
SWORD_ANIM = "Component/AnimationParam/Item_Sword_Biggoron.engine__component__AnimationParam.bgyml"
SWORD_ASINFO = "Component/ASInfo/Item_GetDemo.engine__component__ASInfo.bgyml"
POUCH = "Component/PouchContentParam/WeaponGetTypeMedium.game__component__PouchContentParam.bgyml"
TABLE = "GameParameter/GameParameterTable/Item_Sword_Biggoron.engine__actor__GameParameterTable.bgyml"
FMAB = [{"Fmab": "Work/Model/Weapon/Weapon_Sword_Biggoron/output/Weapon_Sword_Biggoron_Color.fmab"}]
HEART = "Obj_Heart_Piece"
HEART_ELINK = "Component/ELink/Obj_Heart_Piece.engine__component__ELinkParam.bgyml"
HEART_INFO = "Component/ModelInfo/Obj_Heart_Piece.engine__component__ModelInfo.bgyml"


def sword_pack() -> dict[str, bytes]:
    components = {
        "ASInfoRef": "?" + SWORD_ASINFO,
        "ASRef": "?AS/Item_Common.root.asb",
        "ActorNameRef": "?ActorSystem/ActorName/Weapon_Sword_Biggoron.engine__actor__ActorName.bgyml",
        "AnimationRef": "?" + SWORD_ANIM,
        "GameParameterTableRef": "?" + TABLE,
        "ModelInfoRef": "?" + SWORD_INFO,
        "PouchContentRef": "?" + POUCH,
    }
    return {
        actor_member(SWORD): byml.write({"Components": components}),
        SWORD_INFO: byml.write(
            {
                "FmdbName": "Weapon_Sword_Biggoron",
                "ModelProjectName": "Weapon_Sword_Biggoron",
                "ModelVariationAnims": FMAB,
            }
        ),
        SWORD_ANIM: byml.write({"AnimationResources": [{"ModelProjectName": "Weapon_Sword_Biggoron_Animation"}]}),
        SWORD_ASINFO: byml.write({"Default": "Wait"}),
        POUCH: byml.write({"PouchActor": "x"}),
        TABLE: byml.write({}),
    }


def heart_pack() -> dict[str, bytes]:
    components = {
        "AnimationRef": "?Component/AnimationParam/Obj_Heart_Piece.engine__component__AnimationParam.bgyml",
        "ELinkRef": "?" + HEART_ELINK,
        "ModelInfoRef": "?" + HEART_INFO,
    }
    return {
        actor_member(HEART): byml.write({"Components": components}),
        HEART_INFO: byml.write({"FmdbName": "Obj_Heart_Piece", "ModelProjectName": "Obj_Heart_Piece"}),
        "Component/AnimationParam/Obj_Heart_Piece.engine__component__AnimationParam.bgyml": byml.write(
            {"AnimationResources": [{"ModelProjectName": "Obj_Heart_Piece_Animation"}]}
        ),
        HEART_ELINK: byml.write({"UserName": "Obj_Heart_Piece"}),
    }


def built(model=SWORD, pack=sword_pack, **kwargs):
    new = containers.build_pack(donor_pack(), pack(), model, **kwargs)
    members = sarc.read(new.data)
    name = containers.container_name(model)
    return name, new, members, closure([members], name).components


def test_a_container_is_named_from_its_model_and_holds_its_model_under_its_own_member():
    name, new, members, components = built()
    assert name == "Dm_Item_Clawshot_Item_Sword_Biggoron"
    info = "Component/ModelInfo/Dm_Item_Clawshot_Item_Sword_Biggoron.engine__component__ModelInfo.bgyml"
    assert components["ModelInfoRef"] == "?" + info
    assert byml.read(members[info])["FmdbName"] == "Weapon_Sword_Biggoron"
    assert DONOR_INFO not in members and SWORD_INFO not in members  # no shared ModelInfo path is packed
    assert set(members) == set(closure([members], name).members)  # exactly a native-style pack


def test_a_container_has_no_pouch_pickup_ai_or_item_identity():
    _, _, members, components = built()
    assert not {"PouchContentRef", "ActorNameRef", "GameParameterTableRef", "AIRef"} & set(components)
    assert POUCH not in members and TABLE not in members


def test_a_container_takes_the_model_actors_animation_set_and_its_info():
    """Played pilot arm B (BBender, 2026-11-26): Dm_TimeTemple_0130 plays Rotate_GetDemo on its prop, which only an
    item animation set has; containers take the model's own set (D16 revised: scenes that play nothing stay still)."""
    _, new, members, components = built()
    assert components["ASRef"] == "?AS/Item_Common.root.asb"
    assert components["ASInfoRef"] == "?" + SWORD_ASINFO
    assert members[SWORD_ASINFO] == sword_pack()[SWORD_ASINFO]
    assert new.copied[SWORD_ASINFO] == getitem.pack_path(SWORD)


def stone_pack() -> dict[str, bytes]:
    pack = heart_pack()
    document = byml.read(pack[actor_member(HEART)])
    document["Components"]["ASRef"] = "?AS/Dummy.root.asb"
    pack[actor_member(HEART)] = byml.write(document)
    return pack


@pytest.mark.parametrize("pack", [heart_pack, stone_pack], ids=["no set", "dummy set"])
def test_a_container_keeps_the_donors_dummy_set_when_the_model_has_no_animation_set_of_its_own(pack):
    *_, components = built(HEART, pack)
    assert components["ASRef"] == "?AS/DemoDummy.root.asb"
    assert "ASInfoRef" not in components


@pytest.mark.parametrize(
    ("actor", "model"),
    [
        ("Item_Melody_FireBolero", "Item_Melody_FireBolero"),  # its own container: the song's effect (arm B)
        (custom.NOTHING, custom.DONOR),
        (SWORD, SWORD),
    ],
)
def test_a_song_is_its_own_container_model_and_any_other_item_its_get_pose_model(actor, model):
    assert containers.container_model(actor) == model


def test_a_container_keeps_the_model_variation_and_references_the_model_actors_own_animation_param():
    _, new, members, components = built()
    info = members[containers.model_member(containers.container_name(SWORD))]
    assert byml.read(info)["ModelVariationAnims"] == FMAB
    assert components["AnimationRef"] == "?" + SWORD_ANIM
    assert members[SWORD_ANIM] == sword_pack()[SWORD_ANIM]  # read, never edited
    assert new.copied[SWORD_ANIM] == getitem.pack_path(SWORD)


def test_a_container_references_the_model_actors_elink_when_it_has_one_and_none_otherwise():
    *_, components = built(HEART, heart_pack)
    assert components["ELinkRef"] == "?" + HEART_ELINK
    *_, sword = built()
    assert "ELinkRef" not in sword


def test_every_member_but_the_new_ones_is_a_byte_identical_copy_of_its_native_pack():
    name, new, members, _ = built()
    fresh = {actor_member(name), containers.model_member(name)}
    assert set(members) - set(new.copied) == fresh
    for member, source in new.copied.items():
        native = donor_pack() if source == getitem.pack_path(DONOR) else sword_pack()
        assert members[member] == native[member], member


@pytest.mark.parametrize(
    ("actor", "model"),
    [
        ("Item_Melody_FireBolero", getitem.SONG_MODELS["Item_Melody_FireBolero"]),
        (custom.NOTHING, custom.DONOR),
        (custom.FOREIGN.format(index=7), custom.DONOR),
        (SWORD, SWORD),
    ],
)
def test_the_model_is_the_one_the_get_pose_shows(actor, model):
    assert getitem.model_actor(actor) == model


ROW = {"__RowId": DONOR, "FmdbName": "Item_Ocarina_Fairy", "ModelProjectName": "Item_Ocarina_Fairy"}


def rows():
    donor = {
        **ROW,
        "ELinkUserName": "Item_Ocarina_Fairy",
        "InstanceHeapSize": byml.I32(53632),
        "PreActorRenderInfoHeapSize": byml.I32(7536),
        "CalcRadius": byml.F32(40.0),
        "DisplayRadius": byml.F32(40.0),
        "LoadRadius": byml.F32(140.0),
        "ModelAabbMin": {"X": byml.F32(-0.1)},
        "ModelAabbMax": {"X": byml.F32(0.1)},
    }
    sword = {
        "__RowId": SWORD,
        "ActorName": "Weapon_Sword_Biggoron",
        "AnimationResources": [{"ModelProjectName": "Weapon_Sword_Biggoron_Animation"}],
        "FmdbName": "Weapon_Sword_Biggoron",
        "ModelProjectName": "Weapon_Sword_Biggoron",
        "ModelVariationFmabName": "Weapon_Sword_Biggoron_Color",
        "InstanceHeapSize": byml.I32(93768),
        "PreActorRenderInfoHeapSize": byml.I32(7576),
        "CalcRadius": byml.F32(80.0),
        "DisplayRadius": byml.F32(80.0),
        "LoadRadius": byml.F32(180.0),
        "ModelAabbMin": {"X": byml.F32(-0.2)},
        "ModelAabbMax": {"X": byml.F32(1.5)},
    }
    return byml.write([donor, sword])


def test_the_actor_info_row_is_the_donors_with_the_models_fields_and_the_larger_heaps_and_radii():
    out = {r["__RowId"]: r for r in byml.read(containers.actor_info_transform([SWORD])(rows()))}
    row = out["Dm_Item_Clawshot_Item_Sword_Biggoron"]
    assert row["FmdbName"] == "Weapon_Sword_Biggoron" and row["ModelVariationFmabName"] == "Weapon_Sword_Biggoron_Color"
    assert row["AnimationResources"] == [{"ModelProjectName": "Weapon_Sword_Biggoron_Animation"}]
    assert int(row["InstanceHeapSize"]) == 93768 and float(row["LoadRadius"]) == 180.0
    assert "ELinkUserName" not in row and "ActorName" not in row  # no effects user, no item identity
    assert [r["__RowId"] for r in byml.read(containers.actor_info_transform([SWORD])(rows()))] == sorted(
        out, key=str.encode
    )


SONG = "Item_Melody_FireBolero"


def song_rows():
    donor = byml.read(rows())[0]
    song = {
        "__RowId": SONG,
        "ActorName": SONG,
        "FmdbName": "Obj_Rupee",
        "ModelProjectName": "Obj_Rupee",
        "InstanceHeapSize": byml.I32(68168),
        "PreActorRenderInfoHeapSize": byml.I32(7640),
    }
    ocarina = {
        "__RowId": "Item_Ocarina_Time",
        "FmdbName": "Item_Ocarina_Time",
        "ModelProjectName": "Item_Ocarina_Time",
        "ModelAabbMin": {"X": byml.F32(-0.13)},
        "ModelAabbMax": {"X": byml.F32(0.11)},
        "ELinkUserName": "Item_Ocarina_Time",
        "InstanceHeapSize": byml.I32(53632),
        "PreActorRenderInfoHeapSize": byml.I32(7560),
    }
    return byml.write(sorted([donor, song, ocarina], key=lambda r: r["__RowId"].encode()))


def test_a_song_containers_row_shows_its_ocarina_with_the_songs_effect_user_and_heaps():
    """As the song step shows the song (songs.patch_actor_info), whatever the order of the two steps."""
    out = {r["__RowId"]: r for r in byml.read(containers.actor_info_transform([SONG])(song_rows()))}
    row = out["Dm_Item_Clawshot_Item_Melody_FireBolero"]
    assert (row["FmdbName"], row["ModelProjectName"]) == ("Item_Ocarina_Time", "Item_Ocarina_Time")
    assert row["ModelAabbMax"] == {"X": byml.F32(0.11)}
    assert row["ELinkUserName"] == "Clawshot_Song_FireBolero_Event"  # D18: the event user
    assert int(row["InstanceHeapSize"]) == 68168 + 53632 and int(row["PreActorRenderInfoHeapSize"]) == 7640
    assert "ActorName" not in row
    table = byml.read(song_rows())
    native = {r["__RowId"]: r for r in table}
    native[SONG].update(songs.shown_row(native[SONG], native["Item_Ocarina_Time"], SONG))  # the song step ran first
    shown = byml.read(containers.actor_info_transform([SONG])(byml.write(table)))
    assert {r["__RowId"]: r for r in shown}["Dm_Item_Clawshot_Item_Melody_FireBolero"] == row


def test_the_game_actor_info_row_carries_the_models_variation_animations():
    data = byml.write([{"__RowId": DONOR}, {"__RowId": SWORD, "ModelVariationAnims": FMAB}])
    out = {r["__RowId"]: r for r in byml.read(containers.game_actor_info_transform([SWORD])(data))}
    assert out["Dm_Item_Clawshot_Item_Sword_Biggoron"] == {
        "__RowId": "Dm_Item_Clawshot_Item_Sword_Biggoron",
        "ModelVariationAnims": FMAB,
    }


def test_a_container_row_that_exists_already_is_refused():
    once = containers.actor_info_transform([SWORD])(rows())
    with pytest.raises(PatchError):
        containers.actor_info_transform([SWORD])(once)


def test_the_two_new_members_are_sized_from_their_native_donor_members_plus_rounded_growth():
    name, new, members, _ = built()
    param, info = actor_member(name), containers.model_member(name)
    assert set(new.members) == {param, info}
    assert new.members[param][0] == DONOR_PARAM
    assert new.members[info][0] == SWORD_INFO
    for member, (donor, growth) in new.members.items():
        native = (donor_pack() | sword_pack())[donor]
        assert growth == max(0, (len(members[member]) + 31) // 32 * 32 - (len(native) + 31) // 32 * 32)


def test_the_actor_member_grows_enough_for_the_games_formula_when_the_donors_entry_is_known():
    """A container's ActorParam can hold more components than the donor's (the model's animation set), and the game
    sizes an ActorParam per component: byte growth alone falls short (dump: Item_Arrow_Ice 6968 + 96 < 7112)."""
    from clawshot.formats import rstb

    name, new, members, _ = built(donor_entry=5200)
    param = actor_member(name)
    need = rstb.required_size(param, len(members[param]), len(byml.read(members[param])["Components"]))
    donor, growth = new.members[param]
    assert donor == DONOR_PARAM and 5200 + growth == need  # the formula, not less
    name, generous, *_ = built(donor_entry=99999)
    assert generous.members[param] == built()[1].members[param]  # a large entry keeps the rounded growth


def test_a_song_container_names_the_songs_event_user_through_an_elink_member_of_its_own():
    """D18 (Zelda's throw moves the prop's Skl_Root): the container's effect user is the song's event user, through
    its own member (the song's member keeps naming the song's user), sized from the heart container's."""
    name, new, members, components = built(HEART, heart_pack, elink_user="Clawshot_Song_FireBolero_Event")
    link = songs.elink_member(name)
    assert components["ELinkRef"] == "?" + link
    assert byml.read(members[link]) == {"UserName": "Clawshot_Song_FireBolero_Event"}
    assert HEART_ELINK not in members
    assert new.members[link][0] == songs.elink_member(songs.EFFECT_DONOR)
    assert link not in new.copied


def test_native_inputs_name_the_donor_and_each_items_container_model():
    inputs = containers.native_inputs(["Item_Sword_Kokiri", "Item_Melody_StormSong", custom.NOTHING])
    assert getitem.pack_path(containers.DONOR) in inputs
    assert getitem.pack_path("Item_Sword_Kokiri") in inputs
    assert getitem.pack_path("Item_Melody_StormSong") in inputs  # a song's own pack, as the song step shows it
    assert getitem.pack_path(songs.EFFECT_DONOR) in inputs and songs.ELINK in inputs
    assert getitem.pack_path(custom.DONOR) in inputs  # Nothing shows Zelda's Letter
    assert getitem.pack_path(custom.NOTHING) not in inputs
    plain = containers.native_inputs(["Item_Sword_Kokiri"])
    assert songs.ELINK not in plain and getitem.pack_path(songs.EFFECT_DONOR) not in plain
