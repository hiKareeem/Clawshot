"""Containers for every item model against the dump (spec event-items 2.4, 2.8; plan 7.7): no file at a path another
actor reads changes, and the row tables take one new row per model."""

from pathlib import Path

import pytest

from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.patch import containers, event_props, getitem, songs
from clawshot.patch import items as item_actors
from clawshot.patch.actor_packs import actor_member

pytestmark = pytest.mark.dump


@pytest.fixture(scope="module")
def built(romfs):
    models = {containers.container_model(actor) for actor in item_actors.load().actors.values()}
    models |= {containers.container_model(prop.item) for prop in event_props.load().props}
    return containers.changes(romfs, sorted(models)), sorted(models)


def _read(romfs: Path, dicts, path: str) -> bytes:
    return dicts.decompress(path, (romfs / path).read_bytes())


def test_dump_every_container_writes_only_new_paths_and_byte_identical_native_copies(romfs, built):
    (_, packs), models = built
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    table = rstb.read(_read(romfs, dicts, rstb.TABLE_PATH))
    natives: dict[str, dict[str, bytes]] = {}
    for model in models:
        name = containers.container_name(model)
        path = getitem.pack_path(name)
        assert table.get(path) is None and not (romfs / path).exists(), path
        new = packs[path]
        members = sarc.read(new.data)
        fresh = set(members) - set(new.copied)
        own = {actor_member(name), containers.model_member(name)}
        if model in getitem.SONG_MODELS:  # D18: and the event user's ELink member
            own.add(songs.elink_member(name))
        assert fresh == own, (model, sorted(fresh))
        for member in fresh:
            assert table.get(member) is None, f"{member}: a native resource already lives at this path"
        for member, source in new.copied.items():
            if source not in natives:
                natives[source] = sarc.read(_written_song_pack(romfs, dicts, source) or _read(romfs, dicts, source))
            assert natives[source][member] == members[member], (model, member)


def _written_song_pack(romfs: Path, dicts, path: str) -> bytes | None:
    """A song's pack as the song step writes it (a song container copies from it), else None."""
    song = path.removeprefix("Pack/Actor/").removesuffix(".pack.zs")
    if song not in getitem.SONG_MODELS:
        return None
    heart = _read(romfs, dicts, getitem.pack_path(songs.EFFECT_DONOR))
    return songs.patch_song_pack(_read(romfs, dicts, path), song=song, effect_donor=heart)


def test_dump_a_song_container_shows_its_ocarina_with_the_songs_effect_and_the_common_animation_set(romfs, built):
    """Pilot arm B (BBender, 2026-11-26): the Light Arrows scene's Bolero container spins and shows Bolero's effect."""
    (transforms, packs), models = built
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    for song in getitem.SONG_MODELS:
        assert song in models
        name = containers.container_name(song)
        members = sarc.read(packs[getitem.pack_path(name)].data)
        components = byml.read(members[actor_member(name)])["Components"]
        assert components["ASRef"] == "?AS/Item_Common.root.asb", song
        assert components["XLinkRef"] == songs.XLINK and components["ASInfoRef"].startswith("?Component/ASInfo/")
        assert byml.read(members[components["ELinkRef"].lstrip("?")]) == {"UserName": songs.event_user_name(song)}
        info = byml.read(members[containers.model_member(name)])
        assert info["FmdbName"] == info["ModelProjectName"] == getitem.SONG_MODELS[song]
    rows = {
        r["__RowId"]: r
        for r in byml.read(transforms[containers.ACTOR_INFO](_read(romfs, dicts, containers.ACTOR_INFO)))
    }
    row = rows[containers.container_name("Item_Melody_FireBolero")]
    assert row["ELinkUserName"] == "Clawshot_Song_FireBolero_Event" and row["FmdbName"] == "Item_Ocarina_Time"
    from clawshot.formats import elink

    table = elink.decode(transforms[songs.ELINK](_read(romfs, dicts, songs.ELINK)))
    for song in getitem.SONG_MODELS:  # D18: every event user, its GetDemo on Skl_Root
        user = songs.event_user_name(song)
        assert table.has_user(user)
        call = next(k for k, c in enumerate(table.calls(user)) if c.key == "GetDemo")
        if table.calls(user)[call].is_container:
            _, first, last = table.container(user, call)
            bones = {table.call_params(user, k)["Bone"] for k in range(first, last + 1)}
        else:
            bones = {table.call_params(user, call)["Bone"]}
        assert bones == {"Skl_Root"}, song


def test_dump_a_container_takes_its_models_animation_set_or_keeps_the_dummy(romfs, built):
    """D16 revised (BBender, 2026-11-26): the model's own set where it has one (the Light Arrows scene plays
    Rotate_GetDemo on its prop), the donor's dummy where the model's plays nothing (stones, medallions)."""
    (_, packs), models = built
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    sets = {}
    for model in models:
        name = containers.container_name(model)
        sets[model] = byml.read(sarc.read(packs[getitem.pack_path(name)].data)[actor_member(name)])["Components"]
    assert sets["Item_Arrow_Light"]["ASRef"] == "?AS/Item_Common.root.asb"
    assert sets["Obj_Heart_Piece"]["ASRef"] == "?AS/Obj_Heart_Piece.root.asb"
    for model in ("Item_Stone_Water", "Item_Medal_Shadow", "Item_Medal_Light"):
        assert sets[model]["ASRef"] == "?AS/DemoDummy.root.asb" and "ASInfoRef" not in sets[model], model
    table = rstb.read(_read(romfs, dicts, rstb.TABLE_PATH))
    for model in models:  # the writer sizes the ActorParam from the donor's entry plus growth: enough for the game
        name = containers.container_name(model)
        new = packs[getitem.pack_path(name)]
        param = sarc.read(new.data)[actor_member(name)]
        donor, growth = new.members[actor_member(name)]
        need = rstb.required_size(actor_member(name), len(param), len(byml.read(param)["Components"]))
        assert table.get(donor) + growth >= need, (model, table.get(donor), growth, need)


def test_dump_the_row_tables_gain_exactly_one_row_per_container(romfs, built):
    (transforms, _), models = built
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    for path in (containers.ACTOR_INFO, containers.GAME_ACTOR_INFO):
        before = byml.read(_read(romfs, dicts, path))
        after = byml.read(transforms[path](_read(romfs, dicts, path)))
        added = {r["__RowId"] for r in after} - {r["__RowId"] for r in before}
        assert added == {containers.container_name(m) for m in models}, path
        assert len(after) == len(before) + len(models)
        old = {r["__RowId"]: r for r in before}
        assert all(r == old[r["__RowId"]] for r in after if r["__RowId"] in old), path


def test_dump_the_event_users_elink_member_is_sized_from_the_heart_containers_own(romfs):
    """D18: build_pack sizes a song container's ELink member from the effect donor's, taking that member's size as
    a written {UserName: Obj_Heart_Container}: true of the dump's member, by rounded size and content."""
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    heart = sarc.read(_read(romfs, dicts, getitem.pack_path(songs.EFFECT_DONOR)))
    native = heart[songs.elink_member(songs.EFFECT_DONOR)]
    assert byml.read(native) == {"UserName": songs.EFFECT_DONOR}
    assert (len(native) + 31) // 32 == (len(byml.write({"UserName": songs.EFFECT_DONOR})) + 31) // 32
    table = rstb.read(_read(romfs, dicts, rstb.TABLE_PATH))
    assert table.get(songs.elink_member(songs.EFFECT_DONOR)) is not None
