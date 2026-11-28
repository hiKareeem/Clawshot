"""The moat's placed object keeps its actor and shows the given item through its own ModelInfo member (spec event-items
2.5, D5, D14; plan task 10)."""

from clawshot.formats import byml, sarc
from clawshot.patch import placed_models
from clawshot.patch.actor_packs import actor_member, closure

MOAT = "Obj_Ocarina_Time_A_01"
SHARED_INFO = "Component/ModelInfo/Item_Ocarina_Time.engine__component__ModelInfo.bgyml"
ELINK = "Component/ELink/Obj_Ocarina_Time_A_01.engine__component__ELinkParam.bgyml"
AI = "AI/AIInfo/Obj_Ocarina_Time_A_01.engine__actor__AIInfo.bgyml"
SWORD = "Item_Sword_Biggoron"
SWORD_INFO = "Component/ModelInfo/Weapon_Sword_Biggoron.engine__component__ModelInfo.bgyml"
SWORD_ANIM = "Component/AnimationParam/Item_Sword_Biggoron.engine__component__AnimationParam.bgyml"
FMAB = [{"Fmab": "Work/Model/Weapon/Weapon_Sword_Biggoron/output/Weapon_Sword_Biggoron_Color.fmab"}]
HEART = "Obj_Heart_Piece"
HEART_INFO = "Component/ModelInfo/Obj_Heart_Piece.engine__component__ModelInfo.bgyml"


def moat_pack() -> dict[str, bytes]:
    components = {"AIInfoRef": "?" + AI, "ELinkRef": "?" + ELINK, "ModelInfoRef": "?" + SHARED_INFO}
    return {
        actor_member(MOAT): byml.write({"Components": components}),
        SHARED_INFO: byml.write({"FmdbName": "Item_Ocarina_Time", "ModelProjectName": "Item_Ocarina_Time"}),
        ELINK: byml.write({"UserName": MOAT}),
        AI: byml.write({}),
    }


def sword_pack() -> dict[str, bytes]:
    components = {"ModelInfoRef": "?" + SWORD_INFO, "AnimationRef": "?" + SWORD_ANIM}
    return {
        actor_member(SWORD): byml.write({"Components": components}),
        SWORD_INFO: byml.write({"FmdbName": "Weapon_Sword_Biggoron", "ModelVariationAnims": FMAB}),
        SWORD_ANIM: byml.write({"AnimationResources": [{"ModelProjectName": "Weapon_Sword_Biggoron_Animation"}]}),
    }


def heart_pack() -> dict[str, bytes]:
    return {
        actor_member(HEART): byml.write({"Components": {"ModelInfoRef": "?" + HEART_INFO}}),
        HEART_INFO: byml.write({"FmdbName": "Obj_Heart_Piece", "ModelProjectName": "Obj_Heart_Piece"}),
    }


def changed(model=HEART, pack=heart_pack):
    out = sarc.read(placed_models.pack_transform(MOAT, pack(), model)(sarc.write(moat_pack())))
    return out, closure([out], MOAT).components


def test_the_moat_object_keeps_its_actor_and_points_at_a_member_of_its_own_with_the_items_model():
    members, components = changed()
    own = placed_models.member_name(MOAT)
    assert components["ModelInfoRef"] == "?" + own
    assert byml.read(members[own])["FmdbName"] == "Obj_Heart_Piece"
    assert members[SHARED_INFO] == moat_pack()[SHARED_INFO]  # the shared path is never edited
    assert components["AIInfoRef"] == "?" + AI and components["ELinkRef"] == "?" + ELINK  # still the pickup, glow
    assert "AnimationRef" not in components


def test_a_placed_object_takes_the_model_without_its_colour_variation_or_animation():
    """Played runs 08 and 11 and the bisect arms (BBender, 2026-11-26): the Biggoron Sword's colour variation
    (ModelVariationAnims in the object's own ModelInfo) crashes the game on load on a placed object, with or without its
    AnimationRef and rows; the bare model loads and looks normal (arm none). Containers keep the variation (D15)."""
    members, components = changed(SWORD, sword_pack)
    info = byml.read(members[placed_models.member_name(MOAT)])
    assert info["FmdbName"] == "Weapon_Sword_Biggoron" and "ModelVariationAnims" not in info
    assert "AnimationRef" not in components and SWORD_ANIM not in members


def test_the_added_member_is_sized_from_the_packs_native_model_member_plus_rounded_growth():
    before = sarc.write(moat_pack())
    after = placed_models.pack_transform(MOAT, sword_pack(), SWORD)(before)
    own = placed_models.member_name(MOAT)
    added = sarc.read(after)[own]
    growth = max(0, (len(added) + 31) // 32 * 32 - (len(moat_pack()[SHARED_INFO]) + 31) // 32 * 32)
    assert placed_models.added_member_sizes(before, after) == {own: (SHARED_INFO, growth)}
    assert placed_models.added_member_sizes(before, before) == {}


def test_the_rows_take_the_models_visual_fields_and_keep_the_objects_effect_users():
    rows = byml.write(
        [
            {
                "__RowId": MOAT,
                "FmdbName": "Item_Ocarina_Time",
                "ELinkUserName": MOAT,
                "SLinkUserName": MOAT,
                "InstanceHeapSize": byml.I32(51184),
                "LoadRadius": byml.F32(140.0),
            },
            {
                "__RowId": SWORD,
                "FmdbName": "Weapon_Sword_Biggoron",
                "ModelVariationFmabName": "Weapon_Sword_Biggoron_Color",
                "InstanceHeapSize": byml.I32(93768),
                "LoadRadius": byml.F32(180.0),
                "ActorName": "Weapon_Sword_Biggoron",
            },
        ]
    )
    out = {r["__RowId"]: r for r in byml.read(placed_models.actor_info_transform({MOAT: SWORD})(rows))}[MOAT]
    assert out["FmdbName"] == "Weapon_Sword_Biggoron" and "ModelVariationFmabName" not in out  # no variation (08, 11)
    assert (out["ELinkUserName"], out["SLinkUserName"]) == (MOAT, MOAT)
    assert int(out["InstanceHeapSize"]) == 93768 and "ActorName" not in out


STONE = "Obj_InsideJabu_Jabu_Stone_Water_A_01"
STONE_PARENT = "Obj_TimeTemple_SpiritStone_A_03"
PARENT_INFO = "Component/ModelInfo/Obj_TimeTemple_SpiritStone_A_03.engine__component__ModelInfo.bgyml"


def stone_pack() -> dict[str, bytes]:
    """Ruto's stone as the dump has it (plan 10b): its ModelInfoRef comes from its ``$parent``, the Temple of Time's
    Spiritual Stone actor, whose parameter file is in the same pack."""
    parent = f"Work/Actor/{STONE_PARENT}.engine__actor__ActorParam.gyml"
    return {
        actor_member(STONE): byml.write({"$parent": parent, "Components": {"ELinkRef": "?" + ELINK}}),
        actor_member(STONE_PARENT): byml.write({"Components": {"ModelInfoRef": "?" + PARENT_INFO}}),
        PARENT_INFO: byml.write({"FmdbName": "Obj_TimeTemple_SpiritStone", "ModelProjectName": "Obj_TimeTemple"}),
        ELINK: byml.write({"UserName": STONE}),
    }


def test_an_object_whose_model_comes_from_its_parent_gets_a_member_of_its_own_and_the_parent_stays():
    before = sarc.write(stone_pack())
    after = placed_models.pack_transform(STONE, heart_pack(), HEART)(before)
    members = sarc.read(after)
    own = placed_models.member_name(STONE)
    assert closure([members], STONE).components["ModelInfoRef"] == "?" + own
    assert byml.read(members[own])["FmdbName"] == "Obj_Heart_Piece"
    assert members[actor_member(STONE_PARENT)] == stone_pack()[actor_member(STONE_PARENT)]  # the parent is shared
    assert members[PARENT_INFO] == stone_pack()[PARENT_INFO]
    assert placed_models.added_member_sizes(before, after) == {
        own: (PARENT_INFO, max(0, (len(members[own]) + 31) // 32 * 32 - (len(members[PARENT_INFO]) + 31) // 32 * 32))
    }


STONE_RESOURCES = [{"ModelProjectName": "Item_Common_Animation"}, {"ModelProjectName": "Item_Stone_Forest_Animation"}]


def test_the_row_keeps_the_objects_own_animation_resources_and_takes_none_of_the_models():
    """Ruto's stone turns with its own animation resources; the model brings none to a placed object."""
    rows = byml.write(
        [
            {"__RowId": STONE, "FmdbName": "Obj_TimeTemple_SpiritStone", "AnimationResources": STONE_RESOURCES},
            {
                "__RowId": SWORD,
                "FmdbName": "Weapon_Sword_Biggoron",
                "AnimationResources": [{"ModelProjectName": "Weapon_Sword_Biggoron_Animation"}],
            },
            {"__RowId": MOAT, "FmdbName": "Item_Ocarina_Time"},
        ]
    )
    out = {r["__RowId"]: r for r in byml.read(placed_models.actor_info_transform({STONE: SWORD, MOAT: SWORD})(rows))}
    assert out[STONE]["AnimationResources"] == STONE_RESOURCES
    assert "AnimationResources" not in out[MOAT]


def test_the_game_actor_info_row_takes_no_colour_variation():
    data = byml.write(
        [{"__RowId": MOAT, "MainRigidBodyLayer": "GroundHighRes"}, {"__RowId": SWORD, "ModelVariationAnims": FMAB}]
    )
    out = {r["__RowId"]: r for r in byml.read(placed_models.game_actor_info_transform({MOAT: SWORD})(data))}
    assert out[MOAT] == {"__RowId": MOAT, "MainRigidBodyLayer": "GroundHighRes"}
