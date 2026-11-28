"""The song get effects step (``patch/songs.py``) on a synthetic romfs built in code (hard rule 1): the ELink users,
the effect clones, the song packs and rows, the floor pickups, and every native precondition it refuses."""

import math

import pytest
from synthetic_effects import HEART_ACTION_USERS, HEART_USERS, build_bffh, build_table

from clawshot.formats import byml, elink, sarc, vfx, zsdic
from clawshot.patch import getitem, songs
from clawshot.patch.plan import PatchError

EFFECTS = songs.load_effects()
NON_WARP = [s for s, e in EFFECTS.songs.items() if isinstance(e, songs.NonWarpEffect)]
WARP = [s for s, e in EFFECTS.songs.items() if isinstance(e, songs.WarpEffect)]
CHARGE_EMITTERS = ["Spark_Small", "Glow_L", "Glow_Long_00", "LineLight"]
BASE = "Actor/Item_EventObject_Base.engine__actor__ActorParam.bgyml"
ITEM_BASE = "Actor/Obj_Item_Base.engine__actor__ActorParam.bgyml"
PERFORMER = "Component/EventPerformerParam/PouchContent.engine__component__EventPerformerParam.bgyml"
MELODY_POUCH = "Component/PouchContentParam/KeyItemMelody.game__component__PouchContentParam.bgyml"
AS_INFO = "Component/ASInfo/Item_Obj.engine__component__ASInfo.bgyml"


def doc(tree) -> bytes:
    return byml.write(tree)


def song_pack(song: str) -> dict[str, bytes]:
    return {
        BASE: doc({"Components": {"EventPerformerRef": "?" + PERFORMER}}),
        f"Actor/{song}.engine__actor__ActorParam.bgyml": doc(
            {
                "$parent": "Work/Actor/Item_EventObject_Base.engine__actor__ActorParam.gyml",
                "Components": {
                    "ActorNameRef": f"?ActorSystem/ActorName/{song}.engine__actor__ActorName.bgyml",
                    "ModelInfoRef": f"?Component/ModelInfo/{song}.engine__component__ModelInfo.bgyml",
                    "PouchContentRef": "?" + MELODY_POUCH,
                },
            }
        ),
        f"Component/ModelInfo/{song}.engine__component__ModelInfo.bgyml": doc(
            {"FmdbName": "Obj_Rupee", "ModelProjectName": "Obj_Rupee", "Scale": byml.F32(1.0)}
        ),
        MELODY_POUCH: doc({"Category": "KeyItem", "SubCategory": "Melody"}),
        PERFORMER: doc({"Kind": "Pouch"}),
    }


def heart_pack() -> dict[str, bytes]:
    return {
        ITEM_BASE: doc({"Components": {"PhysicsRef": "?Component/Physics/Item.engine__component__PhysicsParam.bgyml"}}),
        "Actor/Obj_Heart_Container.engine__actor__ActorParam.bgyml": doc(
            {
                "$parent": "Work/Actor/Obj_Item_Base.engine__actor__ActorParam.gyml",
                "Components": {"ASInfoRef": "?" + AS_INFO, "ASRef": "?AS/Item_Common.root.asb"},
            }
        ),
        AS_INFO: doc({"Slots": ["Rotate_Obj", "Rotate_GetDemo"]}),
    }


def arrow_pack() -> dict[str, bytes]:
    return {
        ITEM_BASE: doc({"Components": {"PhysicsRef": "?Component/Physics/Item.engine__component__PhysicsParam.bgyml"}}),
        "Actor/Obj_Arrow_Fire.engine__actor__ActorParam.bgyml": doc(
            {
                "$parent": "Work/Actor/Obj_Item_Base.engine__actor__ActorParam.gyml",
                "Components": {
                    "ActorNameRef": "?ActorSystem/ActorName/Item_Arrow_Fire.engine__actor__ActorName.bgyml",
                    "AnimationRef": "?Component/AnimationParam/Obj_Arrow_Fire.engine__component__AnimationParam.bgyml",
                    "ASInfoRef": "?" + AS_INFO,
                    "CaptureRef": "?Component/CaptureParam/Obj_Arrow_Fire.game__component__CaptureParam.bgyml",
                    "ELinkRef": "?Component/ELink/Obj_Arrow_Fire.engine__component__ELinkParam.bgyml",
                    "GameParameterTableRef": "?GameParameter/GameParameterTable/Obj_Arrow_Fire"
                    ".engine__actor__GameParameterTable.bgyml",
                    "ModelInfoRef": "?Component/ModelInfo/Item_Arrow_Fire.engine__component__ModelInfo.bgyml",
                    "PouchContentRef": "?Component/PouchContentParam/ArrowFire"
                    ".game__component__PouchContentParam.bgyml",
                    "SLinkRef": "?Component/SLink/Obj_Arrow_Fire.engine__component__SLinkParam.bgyml",
                    "XLinkRef": songs.XLINK,
                },
            }
        ),
        "Component/AnimationParam/Obj_Arrow_Fire.engine__component__AnimationParam.bgyml": doc(
            {"AnimationResources": [{"ModelProjectName": "Item_Arrow_Fire_Animation"}]}
        ),
        AS_INFO: doc({"Slots": ["Rotate_Obj", "Rotate_GetDemo"]}),
        "Component/ELink/Obj_Arrow_Fire.engine__component__ELinkParam.bgyml": doc({"UserName": "Obj_Arrow_Fire"}),
        "Component/ModelInfo/Item_Arrow_Fire.engine__component__ModelInfo.bgyml": doc({"FmdbName": "Item_Arrow_Fire"}),
        "Component/PouchContentParam/ArrowFire.game__component__PouchContentParam.bgyml": doc(
            {"GetDemoOffsetPos": [byml.F32(0.0), byml.F32(0.2), byml.F32(0.0)], "Category": "Arrow"}
        ),
    }


def row(name: str, **fields) -> dict:
    base = {
        "__RowId": name,
        "FmdbName": name,
        "ModelProjectName": name,
        "ModelAabbMin": [byml.F32(-1.0)] * 3,
        "ModelAabbMax": [byml.F32(1.0)] * 3,
        "InstanceHeapSize": byml.I32(1000),
        "PreActorRenderInfoHeapSize": byml.I32(200),
    }
    base.update(fields)
    return base


def actor_info() -> list[dict]:
    rows = [row("Dm_Item_Ocarina_Fairy_Saria"), row("Item_Arrow_Fire")]
    rows += [row(s, FmdbName="Obj_Rupee", ModelProjectName="Obj_Rupee") for s in getitem.SONG_MODELS]
    rows += [
        row(getitem.FAIRY, CalcPriority="After", InstanceHeapSize=byml.I32(5000)),
        row(getitem.TIME, CalcPriority="After", PreActorRenderInfoHeapSize=byml.I32(900)),
        row(
            "Obj_Arrow_Fire",
            ELinkUserName="Obj_Arrow_Fire",
            SLinkUserName="Obj_Arrow_Fire",
            AnimationResources=[{"ModelProjectName": "Item_Arrow_Fire_Animation"}],
            ActorName="Item_Arrow_Fire",
        ),
    ]
    return sorted(rows, key=lambda r: r["__RowId"].encode())


def game_actor_info() -> list[dict]:
    return [{"__RowId": "Item_Arrow_Fire", "Kind": 1}, {"__RowId": "Obj_Arrow_Fire", "Kind": 2, "Lift": True}]


def pouch_actor_info() -> list[dict]:
    rows = [{"__RowId": s, "Category": "Melody", "SortKey": byml.I32(i)} for i, s in enumerate(getitem.SONG_MODELS)]
    rows.append({"__RowId": "Item_Arrow_Fire", "Category": "Arrow"})
    return sorted(rows, key=lambda r: r["__RowId"].encode())


def static_doc(effects: dict[str, list[str]] | None = None) -> bytes:
    if effects is None:
        effects = {"Ply_Sword_00": ["E0"], songs.CHARGE: CHARGE_EMITTERS}
        effects.update({EFFECTS.songs[s].effect: ["Note"] for s in NON_WARP})
    tree = {"Esets": list(effects), "PtclBin": byml.Binary(build_bffh(effects), 0x1000), "Textures": []}
    return byml.write(tree, version=5)


def native_files() -> dict[str, bytes]:
    files = {
        songs.ELINK: build_table(HEART_USERS),
        songs.STATIC: static_doc(),
        songs.ACTOR_INFO: doc(actor_info()),
        songs.GAME_ACTOR_INFO: doc(game_actor_info()),
        songs.POUCH_ACTOR_INFO: doc(pouch_actor_info()),
        getitem.pack_path(songs.EFFECT_DONOR): sarc.write(heart_pack()),
        getitem.pack_path(songs.PICKUP_DONOR): sarc.write(arrow_pack()),
    }
    for song in getitem.SONG_MODELS:
        files[getitem.pack_path(song)] = sarc.write(song_pack(song))
    return files


def write_romfs(root, zsdic_pack, files: dict[str, bytes]) -> zsdic.Dictionaries:
    dictionaries = zsdic.Dictionaries.from_pack(zsdic_pack)
    (root / zsdic.PACK_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / zsdic.PACK_PATH).write_bytes(zsdic_pack)
    for name, content in files.items():
        rel = name if name.endswith(".zs") else name + ".zs"
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(dictionaries.compress(rel, content))
    return dictionaries


def run(root, zsdic_pack, files=None, *, pickups=True) -> tuple[songs.Delivery, dict[str, bytes]]:
    """Build the step on a synthetic romfs and apply every change to its native file (``pickups``: the full step,
    floor pickups included, which the code keeps for a later feature; seeds build without them)."""
    files = native_files() if files is None else files
    write_romfs(root, zsdic_pack, files)
    delivery = songs.build(root, pickups=pickups)
    out = {}
    for path, transform in delivery.changes.items():
        out[path] = transform(files[path if path in files else path.removesuffix(".zs")])
    return delivery, out


@pytest.fixture
def built(tmp_path, zsdic_pack):
    return run(tmp_path, zsdic_pack)


# ---------------------------------------------------------------------------------------------------------------
# 7.1P ELink users


def users_snapshot(table: elink.Elink, names) -> dict:
    out = {}
    for name in names:
        calls = []
        for k, call in enumerate(table.calls(name)):
            detail = table.container(name, k) if call.is_container else table.call_params(name, k)
            calls.append((call.key, call.asset, call.flag, call.condition, detail))
        out[name] = calls
    return out


def test_elink_adds_twelve_users_copied_from_the_heart_container():
    native = build_table(HEART_USERS)
    before = elink.decode(native)
    out = songs.patch_elink(native, effects=EFFECTS)
    table = elink.decode(out)
    names = [songs.user_name(s) for s in getitem.SONG_MODELS]
    assert sorted(table.user_names()) == sorted(before.user_names() + names)
    assert users_snapshot(table, before.user_names()) == users_snapshot(before, before.user_names())
    heart = before.call_params("Obj_Heart_Container", "Item_Drop")
    for name in names:
        assert table.call_params(name, "Item_Drop") == heart  # calls the step does not set stay as copied


@pytest.mark.parametrize("song", NON_WARP)
def test_non_warp_users_show_their_own_effect(song):
    table = elink.decode(songs.patch_elink(build_table(HEART_USERS), effects=EFFECTS))
    effect = EFFECTS.songs[song]
    wait = table.call_params(songs.user_name(song), "Wait")
    get = table.call_params(songs.user_name(song), "GetDemo")
    assert wait["RuntimeAssetName"] == get["RuntimeAssetName"] == effect.effect
    assert wait["Scale"] == get["Scale"] == pytest.approx(effect.scale)
    assert wait["Bone"] == "Root"  # inherited from the heart container's Wait
    assert get["Bone"] == "Root" and get["PositionY"] == 0.0  # E6: upright and centred in the get pose
    assert "PositionY" not in wait


@pytest.mark.parametrize("song", WARP)
def test_warp_users_play_nine_tinted_children(song):
    table = elink.decode(songs.patch_elink(build_table(HEART_USERS), effects=EFFECTS))
    effect = EFFECTS.songs[song]
    user = songs.user_name(song)
    calls = table.calls(user)
    for key, place, condition in (
        ("Wait", effect.floor, EFFECTS.floor_condition),
        ("GetDemo", effect.get_pose, EFFECTS.get_pose_condition),
    ):
        kind, first, last = table.container(user, key)
        assert kind == 3 and last - first == 8
        children = [table.call_params(user, k) for k in range(first, last + 1)]
        assert [c["RuntimeAssetName"] for c in children] == [songs.SPARK] * 4 + [songs.AURA] * 4 + [songs.LIGHT]
        for i, child in enumerate(children):
            assert calls[first + i].condition == condition and calls[first + i].key == f"{key}_{i:02d}"
            assert child["Bone"] == "Root"
            assert child["Scale"] == pytest.approx(place.scale)
            assert child["PositionY"] == pytest.approx(place.position_y)
            assert child["RotationX"] == pytest.approx(effect.rotation_x)
            assert child["LifeScale"] == pytest.approx(effect.life_scale)
            colour = (place.sparks, place.aura, place.light)[min(i // 4, 2)]
            assert (child["Red"], child["Green"], child["Blue"]) == pytest.approx(colour)
            angle = math.radians(90 * (i % 4))
            radius = effect.ring_radius if i < 8 else 0.0
            assert child["PositionX"] == pytest.approx(radius * math.cos(angle), abs=1e-6)
            assert child["PositionZ"] == pytest.approx(radius * math.sin(angle), abs=1e-6)
    assert [c.asset for c in calls if not c.is_container] == list(range(sum(not c.is_container for c in calls)))


def test_warp_children_keep_the_gallery_order_of_values():
    effect = EFFECTS.songs["Item_Melody_ForestMinuet"]
    children = songs.warp_children(effect, effect.floor)
    assert list(children[0]) == [
        "RuntimeAssetName",
        "PositionX",
        "PositionZ",
        "RotationX",
        "Scale",
        "LifeScale",
        "PositionY",
        "Red",
        "Green",
        "Blue",
    ]
    assert [(c["PositionX"], c["PositionZ"]) for c in children] == [
        (0.12, 0.0),
        (0.0, 0.12),
        (-0.12, 0.0),
        (-0.0, -0.12),
    ] * 2 + [(0.0, 0.0)]
    assert math.copysign(1.0, children[3]["PositionX"]) == -1.0  # -0.0, as the gallery's rounding gives


# ---------------------------------------------------------------------------------------------------------------
# 7.2P effect clones


def test_static_gets_three_clones_with_their_emitters_only():
    native = static_doc()
    out = songs.patch_static(native, effects=EFFECTS)
    blob, before = byml.read(out)["PtclBin"].data, byml.read(native)["PtclBin"].data
    assert vfx.effect_names(blob) == vfx.effect_names(before) + [songs.SPARK, songs.AURA, songs.LIGHT]
    assert vfx.emitters(blob, songs.SPARK) == ["Spark_Small"]
    assert vfx.emitters(blob, songs.AURA) == ["Glow_L", "Glow_Long_00"]
    assert vfx.emitters(blob, songs.LIGHT) == ["LineLight"]
    for name in vfx.effect_names(before):
        assert vfx.effect_bytes(blob, name) == vfx.effect_bytes(before, name)
    vfx.check(blob, dict.fromkeys(songs.CLONES, songs.CHARGE))
    assert byml.read(out)["Esets"] == byml.read(native)["Esets"]


# ---------------------------------------------------------------------------------------------------------------
# 7.3P song packs


@pytest.mark.parametrize("song", getitem.SONG_MODELS)
def test_song_pack_gets_model_animation_effect_user_asinfo_and_xlink(song):
    native = song_pack(song)
    out = sarc.read(songs.patch_song_pack(sarc.write(native), song=song, effect_donor=sarc.write(heart_pack())))
    ocarina = getitem.SONG_MODELS[song]
    param = f"Actor/{song}.engine__actor__ActorParam.bgyml"
    components = byml.read(out[param])["Components"]
    native_components = byml.read(native[param])["Components"]
    anim = getitem.animation_member(song)
    link = songs.elink_member(song)
    assert components == {
        **native_components,
        "ASRef": "?AS/Item_Common.root.asb",
        "AnimationRef": "?" + anim,
        "ELinkRef": "?" + link,
        "ASInfoRef": "?" + AS_INFO,
        "XLinkRef": songs.XLINK,
    }
    model = byml.read(out[f"Component/ModelInfo/{song}.engine__component__ModelInfo.bgyml"])
    assert (model["FmdbName"], model["ModelProjectName"]) == (ocarina, ocarina)
    assert out[anim] == getitem.animation_param(ocarina)
    assert byml.read(out[link]) == {"UserName": songs.user_name(song)}
    assert out[AS_INFO] == heart_pack()[AS_INFO]
    unchanged = set(native) - {param, f"Component/ModelInfo/{song}.engine__component__ModelInfo.bgyml"}
    assert {n: out[n] for n in unchanged} == {n: native[n] for n in unchanged}
    assert set(out) == set(native) | {anim, link, AS_INFO}


# ---------------------------------------------------------------------------------------------------------------
# 7.4P song rows, 7.5P floor pickups


def rows_by_id(data: bytes) -> dict[str, dict]:
    return {r["__RowId"]: r for r in byml.read(data)}


def test_song_rows_get_the_ocarina_model_effect_user_and_heaps():
    native = actor_info()
    out = rows_by_id(songs.patch_actor_info(doc(native)))
    before = {r["__RowId"]: r for r in native}
    for song, ocarina in getitem.SONG_MODELS.items():
        got, donor = out[song], before[ocarina]
        for field in getitem.MODEL_FIELDS:
            assert got[field] == donor[field]
        assert got["ELinkUserName"] == songs.user_name(song)
        assert got["InstanceHeapSize"] == before[song]["InstanceHeapSize"] + donor["InstanceHeapSize"]
        assert type(got["InstanceHeapSize"]) is byml.I32
        assert got["PreActorRenderInfoHeapSize"] == max(
            before[song]["PreActorRenderInfoHeapSize"], donor["PreActorRenderInfoHeapSize"]
        )
    for name in ("Dm_Item_Ocarina_Fairy_Saria", getitem.FAIRY, getitem.TIME, "Obj_Arrow_Fire"):
        assert byml.same(out[name], before[name])


def test_actor_info_works_on_a_table_earlier_steps_changed():
    native = actor_info()
    native.insert(0, row("Aaa_Custom_Item"))  # a row another step inserted
    for r in native:
        if r["__RowId"] in getitem.OCARINAS:
            del r["CalcPriority"]  # as the ocarina get model leaves them
    out = byml.read(songs.patch_actor_info(doc(native)))
    ids = [r["__RowId"] for r in out]
    assert ids == sorted(ids, key=str.encode) and "Aaa_Custom_Item" in ids
    assert all(
        r.get("ELinkUserName") == songs.user_name(r["__RowId"]) for r in out if r["__RowId"] in getitem.SONG_MODELS
    )


def test_pickup_rows_come_from_the_arrow_and_the_song():
    info = rows_by_id(songs.patch_actor_info(doc(actor_info()), pickups=True))
    game = byml.read(songs.patch_game_actor_info(doc(game_actor_info())))
    pouch = byml.read(songs.patch_pouch_actor_info(doc(pouch_actor_info())))
    before = {r["__RowId"]: r for r in actor_info()}
    for table in (list(info.values()), game, pouch):
        ids = [r["__RowId"] for r in table]
        assert ids == sorted(ids, key=str.encode)
    game_ids = {r["__RowId"]: r for r in game}
    pouch_ids = {r["__RowId"]: r for r in pouch}
    native_pouch = {r["__RowId"]: r for r in pouch_actor_info()}
    for song, ocarina in getitem.SONG_MODELS.items():
        pickup = songs.pickup_name(song)
        got = info[pickup]
        arrow = before["Obj_Arrow_Fire"]
        for field in getitem.MODEL_FIELDS:
            assert got[field] == before[ocarina][field]
        assert got["ELinkUserName"] == songs.user_name(song) and got["ActorName"] == song
        assert "SLinkUserName" not in got
        assert got["AnimationResources"] == [
            {"ModelProjectName": getitem.COMMON_ANIMATION},
            {"ModelProjectName": f"{ocarina}_Animation"},
        ]
        assert got["InstanceHeapSize"] == arrow["InstanceHeapSize"]
        assert game_ids[pickup] == {**game_actor_info()[1], "__RowId": pickup}
        assert pouch_ids[pickup] == {**native_pouch[song], "__RowId": pickup}


def test_pickup_pack_is_the_arrow_with_the_song_identity(built):
    delivery, out = built
    arrow = arrow_pack()
    for song, ocarina in getitem.SONG_MODELS.items():
        pickup = songs.pickup_name(song)
        new = delivery.new_files[getitem.pack_path(pickup)]
        pack = sarc.read(new.data)
        param = f"Actor/{pickup}.engine__actor__ActorParam.bgyml"
        tree = byml.read(pack[param])
        components = tree["Components"]
        arrow_tree = byml.read(arrow["Actor/Obj_Arrow_Fire.engine__actor__ActorParam.bgyml"])
        assert tree["$parent"] == arrow_tree["$parent"]
        for dropped in ("GameParameterTableRef", "SLinkRef", "CaptureRef"):
            assert dropped not in components
        model = f"Component/ModelInfo/{song}.engine__component__ModelInfo.bgyml"
        anim = getitem.animation_member(pickup)
        pouch = f"Component/PouchContentParam/{pickup}.game__component__PouchContentParam.bgyml"
        assert components == {
            **{
                k: v
                for k, v in byml.read(arrow["Actor/Obj_Arrow_Fire.engine__actor__ActorParam.bgyml"])[
                    "Components"
                ].items()
                if k not in ("GameParameterTableRef", "SLinkRef", "CaptureRef")
            },
            "ActorNameRef": f"?ActorSystem/ActorName/{song}.engine__actor__ActorName.bgyml",
            "ModelInfoRef": "?" + model,
            "AnimationRef": "?" + anim,
            "PouchContentRef": "?" + pouch,
            "ELinkRef": "?" + songs.elink_member(pickup),
        }
        changed_song = sarc.read(out[getitem.pack_path(song)])
        assert pack[model] == changed_song[model]  # the song's model member as this seed writes it
        assert pack[MELODY_POUCH] == song_pack(song)[MELODY_POUCH]
        assert pack[anim] == getitem.animation_param(ocarina)
        assert byml.read(pack[songs.elink_member(pickup)]) == {"UserName": songs.user_name(song)}
        assert byml.same(
            byml.read(pack[pouch]),
            {
                "$parent": "Work/Component/PouchContentParam/KeyItemMelody.game__component__PouchContentParam.gyml",
                "GetDemoOffsetPos": [byml.F32(0.0), byml.F32(0.2), byml.F32(0.0)],
                "PouchActor": f"Work/Actor/{song}.engine__actor__ActorParam.gyml",
            },
        )
        assert "Actor/Obj_Arrow_Fire.engine__actor__ActorParam.bgyml" not in pack
        for name, content in arrow.items():
            if name != "Actor/Obj_Arrow_Fire.engine__actor__ActorParam.bgyml":
                assert pack[name] == content and new.copied[name] == getitem.pack_path(songs.PICKUP_DONOR)
        assert new.copied[model] == new.copied[MELODY_POUCH] == getitem.pack_path(song)
        assert set(pack) - set(new.copied) == {param, anim, pouch, songs.elink_member(pickup)}


def test_build_changes_exactly_the_feature_files(built):
    delivery, _ = built
    assert sorted(delivery.changes) == sorted(
        [
            songs.ELINK,
            songs.STATIC,
            songs.ACTOR_INFO,
            songs.GAME_ACTOR_INFO,
            songs.POUCH_ACTOR_INFO,
            *(getitem.pack_path(s) for s in getitem.SONG_MODELS),
        ]
    )
    assert sorted(delivery.new_files) == sorted(getitem.pack_path(songs.pickup_name(s)) for s in getitem.SONG_MODELS)
    assert "ELink2/elink2.Product.100.belnk.zs" not in delivery.changes


def test_a_seed_build_writes_no_pickup_pack_or_row(tmp_path, zsdic_pack):
    """Kareem, 2026-11-23 (rounds/r21-pr41.md finding 4): until a feature places the floor pickups, the step a seed
    runs writes none of their packs and no row for them; GameActorInfo and PouchActorInfo stay untouched, and the
    songs' own rows and packs change as with the pickups."""
    seed, seed_out = run(tmp_path / "seed", zsdic_pack, pickups=False)
    full, full_out = run(tmp_path / "full", zsdic_pack)
    assert seed.new_files == {}
    assert sorted(seed.changes) == sorted(set(full.changes) - {songs.GAME_ACTOR_INFO, songs.POUCH_ACTOR_INFO})
    ids = [row["__RowId"] for row in byml.read(seed_out[songs.ACTOR_INFO])]
    assert ids == [row["__RowId"] for row in actor_info()]
    assert not any(i.startswith("Obj_Clawshot_Melody_") for i in ids)
    full_rows = rows_by_id(full_out[songs.ACTOR_INFO])
    assert {i: full_rows[i] for i in ids} == rows_by_id(seed_out[songs.ACTOR_INFO])
    for path in (songs.ELINK, songs.STATIC, *(getitem.pack_path(s) for s in getitem.SONG_MODELS)):
        assert seed_out[path] == full_out[path], path


# ---------------------------------------------------------------------------------------------------------------
# 7.6 / 7.7P native preconditions


def without(path: str):
    def change(files):
        del files[path]

    return change


def edit_rows(path: str, edit):
    def change(files):
        rows = byml.read(files[path])
        edit(rows)
        files[path] = doc(rows)

    return change


def edit_pack(actor: str, edit):
    def change(files):
        pack = sarc.read(files[getitem.pack_path(actor)])
        edit(pack)
        files[getitem.pack_path(actor)] = sarc.write(pack)

    return change


def with_static(effects):
    def change(files):
        files[songs.STATIC] = static_doc(effects)

    return change


def static_effects(**changes) -> dict[str, list[str]]:
    effects = {"Ply_Sword_00": ["E0"], songs.CHARGE: list(CHARGE_EMITTERS)}
    effects.update({EFFECTS.songs[s].effect: ["Note"] for s in NON_WARP})
    for name, value in changes.items():
        if value is None:
            effects.pop(name)
        else:
            effects[name] = value
    return effects


def with_users(users):
    def change(files):
        files[songs.ELINK] = build_table(users)

    return change


def song_model(song, model):
    def edit(pack):
        member = f"Component/ModelInfo/{song}.engine__component__ModelInfo.bgyml"
        pack[member] = doc({"FmdbName": model, "ModelProjectName": model})

    return edit_pack(song, edit)


REJECTIONS = [
    (without(getitem.pack_path("Item_Melody_SunSong")), "Item_Melody_SunSong"),
    (without(getitem.pack_path(songs.EFFECT_DONOR)), "Obj_Heart_Container"),
    (without(getitem.pack_path(songs.PICKUP_DONOR)), "Obj_Arrow_Fire"),
    (
        edit_rows(
            songs.ACTOR_INFO, lambda rows: rows.pop(next(i for i, r in enumerate(rows) if r["__RowId"] == getitem.TIME))
        ),
        "Item_Ocarina_Time",
    ),
    (
        edit_rows(
            songs.ACTOR_INFO,
            lambda rows: rows.pop(next(i for i, r in enumerate(rows) if r["__RowId"] == "Item_Melody_StormSong")),
        ),
        "Item_Melody_StormSong",
    ),
    (
        edit_rows(
            songs.ACTOR_INFO,
            lambda rows: rows.pop(next(i for i, r in enumerate(rows) if r["__RowId"] == "Obj_Arrow_Fire")),
        ),
        "Obj_Arrow_Fire",
    ),
    (edit_rows(songs.GAME_ACTOR_INFO, lambda rows: rows.pop()), "Obj_Arrow_Fire"),
    (
        edit_rows(
            songs.POUCH_ACTOR_INFO,
            lambda rows: rows.pop(next(i for i, r in enumerate(rows) if r["__RowId"] == "Item_Melody_EponaSong")),
        ),
        "Item_Melody_EponaSong",
    ),
    (
        edit_rows(songs.ACTOR_INFO, lambda rows: rows.append(row("Obj_Clawshot_Melody_SunSong"))),
        "Obj_Clawshot_Melody_SunSong",
    ),
    (with_static(static_effects(**{songs.CHARGE: None})), songs.CHARGE),
    (with_static(static_effects(Ply_Ocarina_Correct_StormSong_00=None)), "Ply_Ocarina_Correct_StormSong_00"),
    (with_static(static_effects(**{songs.CHARGE: ["Spark_Small", "Glow_L", "Glow_Long_00"]})), "LineLight"),
    (with_static(static_effects(Clawshot_ChargeAura=["X"])), "Clawshot_ChargeAura"),
    (with_users({k: v for k, v in HEART_USERS.items() if k != songs.EFFECT_DONOR}), "Obj_Heart_Container"),
    (with_users({**HEART_USERS, "Clawshot_Song_SunSong": HEART_USERS["Obj_Rupee_Red"]}), "Clawshot_Song_SunSong"),
    (song_model("Item_Melody_FireBolero", "Item_Ocarina_Time"), "Item_Melody_FireBolero"),
    (edit_pack(songs.EFFECT_DONOR, lambda p: p.pop(AS_INFO)), "Item_Obj"),
    (
        edit_pack("Item_Melody_SunSong", lambda p: p.update({songs.elink_member("Item_Melody_SunSong"): b"x"})),
        "Item_Melody_SunSong",
    ),
]


@pytest.mark.parametrize(("change", "message"), REJECTIONS)
def test_a_changed_native_input_is_refused(tmp_path, zsdic_pack, change, message):
    files = native_files()
    change(files)
    with pytest.raises(PatchError, match=message):
        run(tmp_path, zsdic_pack, files)


def test_a_pickup_pack_already_in_the_dump_is_refused(tmp_path, zsdic_pack):
    files = native_files()
    files[getitem.pack_path("Obj_Clawshot_Melody_SunSong")] = sarc.write(arrow_pack())
    with pytest.raises(PatchError, match="Obj_Clawshot_Melody_SunSong"):
        run(tmp_path, zsdic_pack, files)


# ---------------------------------------------------------------------------------------------------------------
# 7.8P inputs


@pytest.mark.parametrize("pickups", [False, True])
def test_native_inputs_name_every_dump_file_the_step_reads(tmp_path, zsdic_pack, pickups):
    inputs = songs.native_inputs(pickups=pickups)
    assert len(inputs) == len(set(inputs))
    keep = {path.removesuffix(".zs") for path in inputs}
    write_romfs(tmp_path, zsdic_pack, {k: v for k, v in native_files().items() if k.removesuffix(".zs") in keep})
    present = {p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file()}
    assert present == set(inputs)
    assert songs.build(tmp_path, pickups=pickups).changes


def test_the_app_working_set_holds_the_song_inputs():
    from types import SimpleNamespace

    from clawshot.pack.source import resource_spec, working_files

    wanted = working_files(SimpleNamespace(files=[]), resource_spec())
    assert set(songs.native_inputs()) <= wanted, sorted(set(songs.native_inputs()) - wanted)


def test_every_new_member_is_built_in_code(built):
    """7.9P: new members are byml written by the step; everything else is copied from the dump's packs."""
    delivery, _ = built
    for file in delivery.new_files.values():
        for name, content in sarc.read(file.data).items():
            if name not in file.copied:
                assert byml.read(content) is not None


# ---------------------------------------------------------------------------------------------------------------
# 8.1P which seeds get the step


def test_only_a_song_away_from_its_vanilla_place_asks_for_the_song_effects():
    from types import SimpleNamespace

    from clawshot.patch.items import ItemActors

    actors = ItemActors(
        actors={
            "Zeldas Lullaby": "Item_Melody_ZeldaLullaby",
            "Song of Storms": "Item_Melody_StormSong",
            "Bow": "Item_Bow",
        },
        sources={},
    )
    vanilla = {"Song from Impa": "Zeldas Lullaby", "Song from Windmill": "Song of Storms", "Chest A": "Bow"}
    world = SimpleNamespace(locations={name: SimpleNamespace(vanilla=item) for name, item in vanilla.items()})
    assert songs.moved_songs(vanilla, world, actors) == []
    swapped = {**vanilla, "Song from Impa": "Song of Storms", "Song from Windmill": "Zeldas Lullaby"}
    assert songs.moved_songs(swapped, world, actors) == ["Song from Impa", "Song from Windmill"]
    in_chest = {**vanilla, "Chest A": "Zeldas Lullaby", "Song from Impa": "Bow"}
    assert songs.moved_songs(in_chest, world, actors) == ["Chest A"]


@pytest.mark.parametrize(
    ("shuffle", "runs"),
    [
        (("Chest", "Gift"), True),
        (("Gift",), True),
        (("Chest", "NPC", "Song", "Cutscene", "Boss"), True),  # Gift as the types it expands to
        (("Chest",), False),  # the defaults: every song stays home
        (("Chest", "Token"), False),
        ((), False),
    ],
)
def test_song_effects_run_when_the_settings_let_songs_leave_their_places(shuffle, runs):
    assert songs.songs_can_move(shuffle) is runs


# Event containers (event-items D18): the scene's own animation moves an event prop's Skl_Root (Zelda's throw,
# Dm_HrlField_0060: Root has no curves), so a container's effect sits on Skl_Root; at rest the two bones are one
# (Saria's presenting animation). The song actor's own get pose keeps Root (E6).
EVENT_SONGS = ["Item_Melody_SunSong", "Item_Melody_FireBolero"]


def _snapshot_but_bone(table, user):
    """The user's calls with every Bone left out."""
    return [
        (
            key,
            asset,
            flag,
            condition,
            {k: v for k, v in detail.items() if k != "Bone"} if isinstance(detail, dict) else detail,
        )
        for key, asset, flag, condition, detail in users_snapshot(table, [user])[user]
    ]


def test_event_users_are_the_song_users_with_their_effect_on_skl_root():
    native = build_table(HEART_USERS)
    shown = elink.decode(songs.patch_elink(native, effects=EFFECTS))
    table = elink.decode(songs.patch_event_elink(native, songs=EVENT_SONGS, effects=EFFECTS))
    before = elink.decode(native)
    assert sorted(table.user_names()) == sorted(before.user_names() + [songs.event_user_name(s) for s in EVENT_SONGS])
    assert users_snapshot(table, before.user_names()) == users_snapshot(before, before.user_names())
    for song in EVENT_SONGS:
        event, own = songs.event_user_name(song), songs.user_name(song)
        assert event == own + "_Event"
        assert [c.key for c in table.calls(event)] == [c.key for c in shown.calls(own)]
        assert _snapshot_but_bone(table, event) == _snapshot_but_bone(shown, own)
    get = table.call_params(songs.event_user_name("Item_Melody_SunSong"), "GetDemo")
    assert get["Bone"] == songs.EVENT_BONE == "Skl_Root" and get["PositionY"] == 0.0
    user = songs.event_user_name("Item_Melody_FireBolero")
    kind, first, last = table.container(user, "GetDemo")
    assert {table.call_params(user, k)["Bone"] for k in range(first, last + 1)} == {"Skl_Root"}


def test_event_users_and_song_users_go_into_one_table_in_either_order():
    native = build_table(HEART_USERS)
    one = songs.patch_elink(songs.patch_event_elink(native, songs=EVENT_SONGS, effects=EFFECTS), effects=EFFECTS)
    other = songs.patch_event_elink(songs.patch_elink(native, effects=EFFECTS), songs=EVENT_SONGS, effects=EFFECTS)
    names = [*elink.decode(native).user_names(), *map(songs.user_name, getitem.SONG_MODELS)]
    names += [songs.event_user_name(s) for s in EVENT_SONGS]
    for out in (one, other):
        assert sorted(elink.decode(out).user_names()) == sorted(names)


def test_an_event_user_for_something_not_a_song_is_refused():
    with pytest.raises(PatchError):
        songs.patch_event_elink(build_table(HEART_USERS), songs=["Obj_Heart_Piece"], effects=EFFECTS)


# Event-items D20 (pilot A, BBender, runs S12, S13): a scene animation played on a song container (the target's C02,
# Darunia's C09-Gauntlet) starts the event user's get-pose effect, as Rotate_GetDemo does; the emitted key alone did
# not show there (S3, S4, S11).
SCENES = ["Dm_LostWood_0040_Item_BulletBag_Large/C02", "Dm_Goron_0030_Gauntlet_Goron/C09-Gauntlet"]


def test_event_users_start_their_effect_from_each_scene_animation():
    native = build_table(HEART_ACTION_USERS)
    plain = elink.decode(songs.patch_event_elink(native, songs=EVENT_SONGS, effects=EFFECTS))
    table = elink.decode(songs.patch_event_elink(native, songs=EVENT_SONGS, effects=EFFECTS, scene_actions=SCENES))
    for song in EVENT_SONGS:
        user = songs.event_user_name(song)
        assert table.action_triggers(user) == [
            ("AS[Lower]", "Dm_Goron_0030_Gauntlet_Goron/C09-Gauntlet", ["GetDemo"]),
            ("AS[Lower]", "Dm_LostWood_0040_Item_BulletBag_Large/C02", ["GetDemo"]),
            ("AS[Lower]", "Rotate_Obj", ["Wait"]),
            ("Skl[Lower]", "Rotate_GetDemo", ["GetDemo"]),
        ]
        assert plain.action_triggers(user) == elink.decode(native).action_triggers("Obj_Heart_Container")
        assert users_snapshot(table, [user]) == users_snapshot(plain, [user])  # the calls are the same
    names = elink.decode(native).user_names()
    assert {n: table.user_data(n) for n in names} == {n: plain.user_data(n) for n in names}


def test_the_song_users_stay_byte_identical_when_event_users_answer_scene_animations():
    native = songs.patch_elink(build_table(HEART_ACTION_USERS), effects=EFFECTS)
    plain = elink.decode(songs.patch_event_elink(native, songs=EVENT_SONGS, effects=EFFECTS))
    table = elink.decode(songs.patch_event_elink(native, songs=EVENT_SONGS, effects=EFFECTS, scene_actions=SCENES))
    own = [songs.user_name(s) for s in getitem.SONG_MODELS]
    assert {n: table.user_data(n) for n in own} == {n: plain.user_data(n) for n in own}
    assert {n: table.user_data(n) for n in own} == {n: elink.decode(native).user_data(n) for n in own}
    changed = [n for n in table.user_names() if table.user_data(n) != plain.user_data(n)]
    assert sorted(changed) == sorted(songs.event_user_name(s) for s in EVENT_SONGS)


def test_scene_actions_given_twice_or_in_another_order_give_the_same_table():
    native = build_table(HEART_ACTION_USERS)
    one = songs.patch_event_elink(native, songs=EVENT_SONGS, effects=EFFECTS, scene_actions=SCENES)
    other = songs.patch_event_elink(native, songs=EVENT_SONGS, effects=EFFECTS, scene_actions=[*SCENES[::-1], *SCENES])
    assert one == other
