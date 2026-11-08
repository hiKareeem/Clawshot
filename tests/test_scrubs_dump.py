import copy

import pytest

from clawshot.census.scan import GAME_DATA_LIST, read_romfs_byml, scan
from clawshot.formats import evfl, zsdic
from clawshot.patch import scrubs
from clawshot.save import murmur3_32


@pytest.mark.dump
def test_once_sales_change_all_copies_and_tiers_but_no_price_or_saved_gate(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    data = dicts.decompress(scrubs.PATH, (romfs / scrubs.PATH).read_bytes())
    before = evfl.read(data)
    placements = {name: "Item_Boomerang" for name in scrubs.SALES}
    after = evfl.read(scrubs.changes(placements)[scrubs.PATH](data))
    restored = copy.deepcopy(after)
    index = {e.name: e for e in restored.flowchart.events}
    for sale in scrubs.SALES.values():
        for name, old in sale.grants:
            assert index[name].params["ActorName"] == "Item_Boomerang"
            index[name].params["ActorName"] = old
        if sale.selection:
            assert index[sale.selection].params["Value"] == "Item_Boomerang"
            index[sale.selection].params["Value"] = "Obj_Heart_Piece"
    assert restored == before
    gd = read_romfs_byml(romfs, dicts, GAME_DATA_LIST)
    flags = {int(e["Hash"]): e for e in gd["Data"]["Bool"]}
    locations = {loc.id: loc for loc in scan(romfs)}
    for sale in scrubs.SALES.values():
        flag = flags[murmur3_32(sale.flag.encode())]
        assert (int(flag["SaveFileIndex"]), int(flag["ResetTypeValue"])) == (0, 8)
        for actor_id in sale.ids:
            loc = locations[actor_id]
            assert loc.kind == "scrub"
            for path in loc.files:
                tree = read_romfs_byml(romfs, dicts, path)
                actor = next(a for a in tree["Actors"] if int(a["Hash"]) == actor_id)
                entry = actor["Dynamic"]["TalkEventName"]
                settings = read_romfs_byml(romfs, dicts, "RSDB/EventSetting.Product.111.rstbl.byml.zs")
                row = next(r for r in settings if r["__RowId"] == entry)
                assert scrubs.FLOW in row["FlowchartFileName"]
                # Every physical copy still reaches the shared, changed family flow.
                assert any(ep.name == row["EntryPointName"] for ep in after.flowchart.entry_points)
    print(f"four once-sale families / nine actor copies: {len(data)} -> {len(evfl.write(after))} bytes")


@pytest.mark.dump
def test_whole_seed_assigns_one_item_to_every_tier_and_copy_without_changing_prices(romfs, tmp_path):
    from clawshot.generate import Settings
    from clawshot.patch import make_seed, write_seed
    from clawshot.patch.items import load

    output = make_seed(romfs, 7, Settings(shuffle=("Chest", "Scrub")))
    write_seed(output, romfs, tmp_path / "seed")
    dicts, actors = zsdic.Dictionaries.from_romfs(romfs), load()
    data = dicts.decompress(scrubs.PATH, (romfs / scrubs.PATH).read_bytes())
    written = dicts.decompress(scrubs.PATH, (tmp_path / "seed" / "romfs" / scrubs.PATH).read_bytes())
    before, after = evfl.read(data), evfl.read(written)
    index = {e.name: e for e in after.flowchart.events}
    assert set(output.seed.shuffled) & scrubs.SALES.keys() == scrubs.SALES.keys()
    for check, sale in scrubs.SALES.items():
        item = actors.actor(output.seed.placements[check])
        for name, old in sale.grants:
            assert index[name].params["ActorName"] == item
            assert index[name].params["Price"] == sale.price
            index[name].params["ActorName"] = old
        if sale.selection:
            assert index[sale.selection].params["Value"] == item
            index[sale.selection].params["Value"] = "Obj_Heart_Piece"
    assert after == before
    for name in output.seed.shuffled:
        if output.seed.placements[name] in scrubs.CAPACITIES:
            assert name in scrubs.SALES
