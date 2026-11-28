"""Gold Skulltula reward delivery against the player's real dump (``OOT_ROMFS``): native identities, saved collection
rows, the enemy and token contracts, every admitted reward member's native grant shape and generated pickup, the
core delivery and a production Token seed written by the common writer, each compared with the original dump, never
a patched fixture. Data and structure evidence only; gameplay is Kareem's Longshot packets."""

import copy
import functools
from pathlib import PurePosixPath

import pytest

from clawshot.census.scan import GAME_DATA_LIST, GOLD_SKULLTULA, scan
from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.generate import Settings
from clawshot.generate import tokens as token_policy
from clawshot.patch import (
    actor_packs,
    containers,
    event_props,
    getitem,
    items,
    make_seed,
    saria_farewell,
    tokens,
    write_seed,
)
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import write
from clawshot.save import murmur3_32

pytestmark = pytest.mark.dump

TREE, TOWER, LONE = 341792603838029977, 2730878115209290675, 2177746409373494991  # LLR tree/tower, HF lone tree
CORE = {TREE: "Item_Boomerang", TOWER: "Obj_Shield_Hylian", LONE: "Item_Token_Gold"}
CORE_REWARDS = {"Item_Boomerang": "fixed_major", "Obj_Shield_Hylian": "equipment", "Item_Token_Gold": "token"}
CANONICAL = {"Item_Boomerang": "Item_Boomerang", "Obj_Shield_Hylian": "Weapon_Shield_Hylian"}
PRODUCTION = {actor: family for actor, family in token_policy.REWARDS.values()}
# Members whose donor is in the dump; the generated ones (tokens.GENERATED_PREFIX, the ocarina and song world actors a
# seed creates) have no dump row and are checked by test_ocarina_song_drops_dump.py.
NATIVE_PRODUCTION = {a: f for a, f in PRODUCTION.items() if not a.startswith(tokens.GENERATED_PREFIX)}


@pytest.fixture(scope="module")
def production_seed(romfs):
    return make_seed(romfs, 7, Settings(shuffle=("Chest", "Token")))


@pytest.fixture(scope="module")
def census(romfs):
    return [location for location in scan(romfs) if location.kind == GOLD_SKULLTULA]


@pytest.fixture(scope="module")
def original(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def read(path, root=romfs):
        data = (root / path).read_bytes()
        return dictionaries.decompress(path, data) if path.endswith(".zs") else data

    return read


def pouch_of(sources, components):
    """An actor's effective pouch component."""
    reference = actor_packs.reference(components["PouchContentRef"])
    return actor_packs.resolve_node(sources, reference, builtin=tokens.POUCH_DEFAULT)


def actor_name(path):
    return PurePosixPath(actor_packs.reference(path)).name.split(".", 1)[0]


def test_every_delivery_input_is_in_this_romfs(romfs):
    inputs = tokens.native_inputs(PRODUCTION)
    missing = [path for path in inputs if not (romfs / path).is_file()]
    print(f"{len(inputs)} delivery inputs: {list(inputs)}")
    assert missing == [], f"Gold Skulltula delivery inputs missing from this romfs or working set: {missing}"


def test_native_sources_copies_and_saved_collection_rows(romfs, census, original):
    assert len(census) == 100
    assert sum(len(location.files) for location in census) == 114
    for location in census:
        assert location.actor == tokens.ENEMY and location.has_save_flag, location
        for path in location.files:
            placed = [a for a in byml.read(original(path))["Actors"] if a.get("Hash") == location.id]
            assert len(placed) == 1, (path, location.id)
            dynamic = placed[0].get("Dynamic") or {}
            drop = {key: value for key, value in dynamic.items() if str(key).startswith(tokens.DROP_FIELDS)}
            assert (placed[0]["Gyaml"], drop) == (tokens.ENEMY, {}), (path, location.id, drop)
    tokens.check_save_rows(byml.read(original(GAME_DATA_LIST)), [location.id for location in census])
    print("100 sources / 114 copies; 200 permanent collection rows (H and H xor 2); no native drop selector")


def test_native_enemy_and_token_contracts_resolve_semantically(romfs):
    native = tokens.Romfs(romfs)
    tokens.check_source(native)
    pack = tokens.check_token(native)
    token = actor_packs.closure([pack], tokens.TOKEN).components
    picked = tokens.death_procedures(native, pack, token["DeathRef"])["PickedUp___Data"]
    enemy = native.pack(tokens.ENEMY)
    components = actor_packs.resolve([enemy], actor_packs.actor_member(tokens.ENEMY))[0]["Components"]
    life = tokens.death_procedures(native, enemy, components["DeathRef"])["LifeDepleted___Data"]
    print(f"token PickedUp {picked}\nenemy LifeDepleted {life}")
    assert picked["IsWaitForSignal"] is True  # collection waits for the reason-10 callback's signal
    # A kill retires the instance and saves nothing.
    assert (life["IsSetGmdRespawnFlagToFalse"], life["IsSetRespawnFlagToFalse"]) == (False, True)
    assert tokens.source_hash_keys([pack], token) == [
        {"BBKey": tokens.SOURCE_HASH_KEY, "InitVal": 0, "IsInstanceParam": False}
    ]
    assert set(native.inputs) <= set(tokens.NATIVE_INPUTS)


def check_written_delivery(romfs, census, original, out, placements, rewards):
    """Build and write ``placements`` with the common writer, then compare every output with the original dump:
    only the selectors on the assigned sources' copies, new registry rows and size entries, and generated packs whose
    mechanism is the token's and whose identity and grant are the donor's. Returns item -> (canonical, grant)."""
    delivery = tokens.build(romfs, placements, census, rewards=rewards)
    assert set(delivery.inputs) <= set(tokens.native_inputs(rewards))
    written = write(Plan([], [], []), romfs, out, extra_changes=(delivery.changes,), new_files=delivery.new_files)

    def output(path):
        return original(path, out / "romfs")

    locations = {location.id: location for location in census}
    banc = sorted({path for source in delivery.drops for path in locations[source].files})
    created = set(delivery.new_files)
    paths = {info.path for info in written}
    assert paths == {*banc, *tokens.REGISTRIES, rstb.TABLE_PATH, *created}
    assert all(info.entry is None and info.size == 0 for info in written if info.path in created)
    assert not paths & {tokens.TOKEN_PACK, tokens.ENEMY_PACK, "Pack/AI.Global.Product.111.pack.zs"}

    for path in banc:  # only the selector on the assigned sources' copies; Hash, links, groups, appearance native
        before, after = byml.read(original(path)), byml.read(output(path))
        for placed in after["Actors"]:
            if int(placed["Hash"]) in delivery.drops:
                assert placed["Dynamic"].pop(tokens.DROP) == delivery.drops[int(placed["Hash"])]
                if not next(a for a in before["Actors"] if a["Hash"] == placed["Hash"]).get("Dynamic"):
                    assert placed.pop("Dynamic") == {}
        assert byml.same(before, after), path

    names = set(delivery.pickups.values())
    tables = {path: byml.read(output(path)) for path in tokens.REGISTRIES}
    ids = {path: [row["__RowId"] for row in table] for path, table in tables.items()}
    assert ids[tokens.ACTOR_INFO] == ids[tokens.GAME_ACTOR_INFO]
    for path, table in tables.items():
        assert byml.same([row for row in table if row["__RowId"] not in names], byml.read(original(path))), path
    rows = {path: {row["__RowId"]: row for row in table} for path, table in tables.items()}
    native_rows = {path: {row["__RowId"]: row for row in byml.read(original(path))} for path in tokens.REGISTRIES}

    natives = {actor: sarc.read(original(tokens.pack_path(actor))) for actor in (tokens.TOKEN, *delivery.pickups)}
    token = actor_packs.closure([natives[tokens.TOKEN]], tokens.TOKEN).components
    token_pouch = pouch_of([natives[tokens.TOKEN]], token)
    native = tokens.Romfs(romfs)
    token_death = tokens.death_procedures(native, natives[tokens.TOKEN], token["DeathRef"])
    game_data = byml.read(original(GAME_DATA_LIST))
    saved = {int(e["Hash"]) for kind, rows_ in game_data["Data"].items() if kind != "Bool64bitKey" for e in rows_}
    native_table = rstb.read(original(rstb.TABLE_PATH))
    expected_table = copy.deepcopy(native_table)
    for info in written:
        if info.path not in created and info.path != rstb.TABLE_PATH:
            need = rstb.required_size(info.path, info.new_size)
            expected_table.set(info.path, max(native_table.get(info.path), need))

    grants = {}
    for item, pickup in sorted(delivery.pickups.items()):
        path = tokens.pack_path(pickup)
        file = delivery.new_files[path]
        assert output(path) == file.data
        pack = sarc.read(file.data)
        sources = {source: sarc.read(original(source)) for source in set(file.copied.values())}
        for name, source in file.copied.items():
            assert sources[source][name] == pack[name], (name, source)
        found = actor_packs.closure([pack], pickup)
        assert set(found.members) == set(pack)
        effective = found.components
        donor = actor_packs.closure([natives[item]], item).components
        # Mechanism: the token's pinned graph, source-Hash blackboard and death procedures, unchanged.
        assert pack[tokens.TOKEN_GRAPH] == natives[tokens.TOKEN][tokens.TOKEN_GRAPH]
        assert tokens.source_hash_keys([pack], effective) == tokens.source_hash_keys([natives[tokens.TOKEN]], token)
        attention = ("BlackboardParamBoolArray", tokens.ATTENTION_KEY)
        assert tokens.blackboard_entries([pack], effective, *attention) == [
            {"BBKey": tokens.ATTENTION_KEY, "InitVal": True, "IsInstanceParam": False}
        ]
        controllers, bodies = tokens.physics_bodies([pack], effective)
        assert tokens.PHYSICS_BODY in controllers and tokens.PHYSICS_BODY in bodies
        assert tokens.death_procedures(native, pack, effective["DeathRef"]) == token_death
        # Identity: canonical name, pouch grant, registry row and the granted item's own saved record agree; the pouch
        # is the donor's (category, get type, special deal, bundle, caps) but for the pickup policy and grant.
        pouch, native_pouch = pouch_of([pack], effective), pouch_of([natives[item]], donor)
        ignored = {*tokens.POLICY, tokens.GRANT_KEY}
        assert {k: v for k, v in pouch.items() if k not in ignored} == {
            k: v for k, v in native_pouch.items() if k not in ignored
        }
        row = rows[tokens.ACTOR_INFO][pickup]
        assert tokens.canonical(effective) == row["ActorName"] == tokens.canonical(donor)
        if pouch.get(tokens.GRANT_KEY):
            grant = actor_name(pouch[tokens.GRANT_KEY])
            recorded = [grant]
        else:  # a bundle naming none, as its native does: N of its BundleActor, the canonical name recorded
            assert pouch[tokens.BUNDLE_KEY] is True and not native_pouch.get(tokens.GRANT_KEY)
            grant = None
            recorded = [tokens.canonical(donor), actor_name(pouch["BundleActor"])]
        for name in recorded:
            assert name in native_rows[tokens.POUCH_ACTOR_INFO] and murmur3_32(f"IsGet.{name}".encode()) in saved
        assert pouch.get("SpecialDeal") != token_pouch["SpecialDeal"]  # never token stock
        assert all(pouch.get(key) == value for key, value in tokens.POLICY.items())
        model = byml.read(pack[actor_packs.reference(effective["ModelInfoRef"])])
        animation = byml.read(pack[actor_packs.reference(effective["AnimationRef"])])
        assert (row["FmdbName"], row["ModelProjectName"]) == (model["FmdbName"], model["ModelProjectName"])
        assert byml.same(row["AnimationResources"], animation["AnimationResources"])
        assert byml.same(
            {**rows[tokens.POUCH_ACTOR_INFO][pickup], "__RowId": item},
            native_rows[tokens.POUCH_ACTOR_INFO][item],
        )
        assert byml.same(
            {**rows[tokens.GAME_ACTOR_INFO][pickup], "__RowId": tokens.TOKEN},
            native_rows[tokens.GAME_ACTOR_INFO][tokens.TOKEN],
        )
        # Allocation: the pack and each member new to the game get measured entries; copies keep native ones.
        expected_table.set(path, rstb.required_size(path, len(file.data)))
        for name, content in pack.items():
            if name in file.copied:
                assert native_table.get(name) is not None, name
            else:
                assert native_table.get(name) is None, name
                components = len(byml.read(content)["Components"]) if name.endswith(rstb.ACTOR_PARAM) else None
                expected_table.set(name, rstb.required_size(name, len(content), components))
        grants[item] = (tokens.canonical(effective), grant)
        print(f"{pickup}: grants {grant}; {len(pack)} members, {len(pack) - len(file.copied)} new, {len(file.data)} B")
    assert rstb.read(output(rstb.TABLE_PATH)) == expected_table
    return delivery, grants


def test_core_delivery_written_and_compared_with_the_original_dump(romfs, census, original, tmp_path):
    delivery, grants = check_written_delivery(romfs, census, original, tmp_path / "out", CORE, CORE_REWARDS)
    assert delivery.drops == {
        TREE: tokens.pickup_name("Item_Boomerang"),
        TOWER: tokens.pickup_name("Obj_Shield_Hylian"),
    }
    assert grants == {item: (name, name) for item, name in CANONICAL.items()}


def grant_fields(row):
    """The grant fields a donor world pickup must share with the item's chest actor."""
    keys = ("BundleActor", "BundleActorNum", "PouchGetType", "PouchSpecialDeal", "BottleItem", "MPMax")
    return {key: row.get(key) for key in keys}


def test_every_admitted_member_has_its_native_shape_and_a_checked_pickup(romfs, census, original, tmp_path):
    """Every token_rewards.toml member: its dump row has the declared family's shape, the members together covering
    every native grant family; a member of a family admitted after the core packet grants as its chest actor does;
    and its generated pickup (one source each) passes every written-output check, granting a bundle exactly where its
    row names a BundleActor. Structure only: members beyond each family's played representative are unplayed."""
    table = items.load()
    rows = {row["__RowId"]: row for row in byml.read(original(tokens.POUCH_ACTOR_INFO))}
    shapes = {actor: tokens.grant_family(rows[actor]) for actor in NATIVE_PRODUCTION}
    print(f"native shapes {shapes}")
    assert shapes == NATIVE_PRODUCTION
    assert set(PRODUCTION.values()) == token_policy.ADMITTED_FAMILIES == set(tokens.FAMILIES)
    for item, (actor, family) in token_policy.REWARDS.items():
        if family in CORE_REWARDS.values() or actor not in NATIVE_PRODUCTION:
            continue  # the core packet's families, played with their own actors; generated donors (above)
        chest = table.actor(item)
        assert tokens.grant_family(rows[chest]) == family, (item, actor, chest)
        assert grant_fields(rows[actor]) == grant_fields(rows[chest]), item
    members = sorted(actor for actor in NATIVE_PRODUCTION if actor != "Item_Token_Gold")
    sources = sorted(location.id for location in census)
    placements = {**dict(zip(sources, members, strict=False)), sources[-1]: "Item_Token_Gold"}
    delivery, grants = check_written_delivery(romfs, census, original, tmp_path / "out", placements, NATIVE_PRODUCTION)
    assert sorted(delivery.pickups) == members
    assert len(delivery.new_files) == len(members)
    print(f"grants {grants}")
    bundles = {actor for actor, (_, grant) in grants.items() if grant is None}
    assert bundles == {actor for actor in members if rows[actor].get("BundleActor")}


def test_fairy_ocarina_is_excluded_for_want_of_its_own_animation(romfs):
    """The documented ocarina boundary: the Item_ ocarinas (Common performer; Fairy Ocarina has no world pickup) have
    no AnimationRef to give a pickup, so they compose nothing; Ocarina of Time goes through Obj_Ocarina_Time. The
    family is admitted by that member alone: Fairy Ocarina has the same native shape and stays out."""
    native = tokens.Romfs(romfs)
    token = tokens.check_token(native)
    registries = {path: {row["__RowId"]: row for row in byml.read(native.read(path))} for path in tokens.REGISTRIES}
    generic = native.pack(tokens.GENERIC_DISPLAY)
    for item in ("Item_Ocarina_Fairy", "Item_Ocarina_Time"):
        with pytest.raises(PatchError, match=f"{item}: no AnimationRef to give the pickup"):
            tokens.compose(item, token, native.pack(item), generic, registries)
    assert tokens.grant_family(registries[tokens.POUCH_ACTOR_INFO]["Item_Ocarina_Fairy"]) == "ocarina"
    assert "Obj_Ocarina_Fairy" not in registries[tokens.ACTOR_INFO]  # no world pickup to donate


def test_every_source_copy_accepts_a_generated_pickup(romfs, census, original):
    rewards = ("Item_Boomerang", "Obj_Shield_Hylian")
    placements = {location.id: rewards[i % 2] for i, location in enumerate(census)}
    delivery = tokens.build(romfs, placements, census, rewards=CORE_REWARDS)
    assert len(delivery.new_files) == 2
    copies = 0
    for path, transform in delivery.changes.items():
        if path in tokens.REGISTRIES:
            continue
        data = original(path)
        before, after = byml.read(data), byml.read(transform(data))
        for placed in after["Actors"]:
            if int(placed["Hash"]) in delivery.drops:
                assert placed["Dynamic"].pop(tokens.DROP) == delivery.drops[int(placed["Hash"])]
                copies += 1
                native = next(a for a in before["Actors"] if a["Hash"] == placed["Hash"])
                if "Dynamic" not in native:
                    assert placed.pop("Dynamic") == {}
        assert byml.same(before, after), path
    assert copies == 114
    print(f"100 sources / {copies} copies: exact field diff, not gameplay proof")


def test_production_token_seed_writes_only_source_selectors_and_pickups(
    romfs, census, original, production_seed, tmp_path
):
    """A real Chest+Token seed through make_seed and write_seed: every live Skulltula is one Token check linked to its
    census source, the pool keeps one token per live source, and each source's copies either stay native (token) or
    name the generated pickup of the placed reward; nothing global changes."""
    output = production_seed
    seed = output.seed
    token_checks = sorted(name for name in seed.shuffled if seed.world.locations[name].type == token_policy.SHUFFLE)
    rows = output.spoiler()["patch"]["tokens"]
    assert [row["location"] for row in rows] == token_checks
    assert len({row["id"] for row in rows}) == len(rows) == len(token_checks)
    assert sum(seed.placements[name] == token_policy.TOKEN_ITEM for name in seed.shuffled) == len(token_checks)
    by_id = {location.id: location for location in census}
    print(f"{len(rows)} Token checks")
    # All 100 census sources, the three remake-only routes included (Claude, 2026-11-14): none stays native.
    assert {int(row["id"]) for row in rows} == set(by_id)
    for row in rows:
        location = by_id[int(row["id"])]
        assert row["files"] == list(location.files)
        assert token_policy.REWARDS[row["item"]][0] == row["pickup"]
        assert (row["drop_actor"] is None) == (row["pickup"] == "Item_Token_Gold")
    out = tmp_path / "seed"
    written = {info.path for info in write_seed(output, romfs, out)}
    assert not written & {tokens.TOKEN_PACK, tokens.ENEMY_PACK, "Pack/AI.Global.Product.111.pack.zs"}
    assert not any(path.startswith("RSDB/Tag.") for path in written)
    expected = {row["drop_actor"] for row in rows} - {None}
    pickups = {path for path in output.new_files if PurePosixPath(path).name.startswith(tokens.PICKUP_PREFIX)}
    assert pickups == {tokens.pack_path(actor) for actor in expected} <= written
    drops = {int(row["id"]): row["drop_actor"] for row in rows}
    for location in census:  # every copy of every source: the selector the spoiler names, or none at all
        for path in location.files:
            source = out / "romfs" / path
            tree = byml.read(original(path, out / "romfs") if source.is_file() else original(path))
            placed = next(a for a in tree["Actors"] if a.get("Hash") == location.id)
            native = next(a for a in byml.read(original(path))["Actors"] if a.get("Hash") == location.id)
            assert (placed.get("Dynamic") or {}).get(tokens.DROP) == drops.get(location.id), (path, location.id)
            if drops.get(location.id) is not None:
                placed["Dynamic"].pop(tokens.DROP)
                if not native.get("Dynamic"):
                    placed.pop("Dynamic")
            assert byml.same(placed, native), (path, location.id)
    ids = [row["__RowId"] for row in byml.read(original(tokens.ACTOR_INFO, out / "romfs"))]
    assert {name for name in ids if name.startswith(tokens.PICKUP_PREFIX)} == expected


def _module(transform) -> str:
    """The module a transform comes from (a partial counts as its function)."""
    while isinstance(transform, functools.partial):
        transform = transform.func
    return transform.__module__


def test_token_off_seed_has_no_token_output(romfs):
    output = make_seed(romfs, 7, Settings())
    assert output.token_sources == ()
    assert not any(PurePosixPath(path).name.startswith(tokens.PICKUP_PREFIX) for path in output.new_files)
    assert "tokens" not in output.spoiler()["patch"]
    # Other steps edit GameActorInfo too (event-items: event containers, Saria's farewell actor); none of them is the
    # token step.
    touching = [
        changes[tokens.GAME_ACTOR_INFO] for changes in output.extra_changes if tokens.GAME_ACTOR_INFO in changes
    ]
    assert not any(_module(transform) == tokens.__name__ for transform in touching)
    assert token_policy.SHUFFLE not in {location.type for location in output.seed.world.locations.values()}


def test_custom_chest_items_and_token_pickups_write_one_valid_set_of_tables(romfs, original, production_seed, tmp_path):
    from clawshot.generate.fill import allowed
    from clawshot.patch.custom_items import NOTHING, TABLES, Foreign

    seed = production_seed.seed
    placements = {name: seed.placements[name] for name in seed.shuffled}
    eligible = sorted(
        {
            change.location
            for change in production_seed.plan.changes
            if not seed.world.items[placements[change.location]].progression
            and change.event is None
            and change.kept_event is None
            and change.key_event is None
            and change.dungeon_item is None
            and all(
                allowed(seed.world, seed.settings, change.location, item) for item in ("Nothing", "Archipelago Item")
            )
        }
    )
    assert len(eligible) >= 2, eligible
    placements[eligible[0]], placements[eligible[1]] = "Nothing", "Archipelago Item"
    output = make_seed(
        romfs,
        seed.seed,
        seed.settings,
        placements=placements,
        foreign={eligible[1]: Foreign("Other player", "Other item")},
    )
    generated = {row.drop_actor for row in output.token_sources} - {None}
    expected = {NOTHING, "Item_Clawshot_AP_000"} | generated
    event_items = {saria_farewell.pack_path(saria_farewell.FAREWELL)}  # every seed (event-items D9)
    actor_packs = {
        path
        for path in output.new_files
        if path.startswith("Pack/Actor/")
        and path not in event_items
        and not path.startswith(f"Pack/Actor/{containers.PREFIX}")  # event containers (event-items)
    }
    assert generated and actor_packs == {tokens.pack_path(actor) for actor in expected}
    before = {path: original(path) for path in TABLES}
    out = tmp_path / "combined"
    write_seed(output, romfs, out)
    for path in TABLES:
        native = {row["__RowId"]: row for row in byml.read(before[path])}
        # A seed whose settings can put an ocarina in a chest also carries the ocarina get model, its only change to
        # native rows.
        if path == getitem.ACTOR_INFO and any(
            step.get(path) is getitem.patch_ocarina_actor_info for step in output.extra_changes
        ):
            for actor in getitem.OCARINAS:
                assert native[actor].pop("CalcPriority") == "After", actor
            assert "CalcPriority" not in native[getitem.SARIA_PROP]
            native[getitem.SARIA_PROP]["CalcPriority"] = "After"
        rows = byml.read(original(path, out / "romfs"))
        ids = [row["__RowId"] for row in rows]
        assert ids == sorted(set(ids))
        # event-items: the bridge Saria's own actor (every seed) and the event containers of moved gifts add rows;
        # the placed objects (moat, Ruto's stone) take their shown model's fields in their own native rows.
        event_rows = {saria_farewell.FAREWELL} | {i for i in ids if i.startswith(containers.PREFIX)}
        placed = {prop.actor for prop in event_props.load().props if prop.part == event_props.PLACEMENT}
        assert set(ids) == native.keys() | expected | (event_rows & set(ids))
        assert saria_farewell.FAREWELL in ids or path not in (getitem.ACTOR_INFO, tokens.GAME_ACTOR_INFO), path
        actual = {row["__RowId"]: row for row in rows}
        assert all(byml.same(row, actual[name]) for name, row in native.items() if name not in placed), path
        assert original(path) == before[path]
    old_sizes = rstb.read(original(rstb.TABLE_PATH))
    sizes = rstb.read(original(rstb.TABLE_PATH, out / "romfs"))
    assert rstb.read(rstb.write(sizes)) == sizes
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for path, file in output.new_files.items():
        content = (out / "romfs" / path).read_bytes()
        if path.endswith(".zs"):  # a loose file (event-items: Saria's schedule list) is written as it is
            content = dictionaries.decompress(path, content)
        assert content == file.data
        if file.sized_like is not None:  # no size formula: its native donor's entry plus the growth
            donor, growth = file.sized_like
            assert sizes.get(path) == old_sizes.get(donor) + growth, path
        else:
            assert sizes.get(path) == rstb.required_size(path, len(content))
        assert not (romfs / path).exists()
        if not path.endswith(".pack.zs"):
            continue  # non-pack resources still receive the byte, native-absence and allocation checks above
        for name, data in sarc.read(content).items():
            if name in file.members:
                donor, growth = file.members[name]
                expected_size = old_sizes.get(donor) + growth
            elif name in file.copied or file.members:
                expected_size = old_sizes.get(name)
            else:
                components = len(byml.read(data)["Components"]) if name.endswith(rstb.ACTOR_PARAM) else None
                expected_size = rstb.required_size(name, len(data), components)
            assert expected_size is not None and sizes.get(name) == expected_size, name
