"""A wrongly classified native age would hide a needed reload warning."""

import tomllib

import pytest

from clawshot.formats import byml
from clawshot.generate.itembar import CATALOG

pytestmark = pytest.mark.dump


def test_warning_ages_agree_with_every_native_ui_variant(romfs):
    path = romfs / "UI/Pouch/PouchTable/PouchTable.game__ui__PouchTable.bgyml"
    layout = byml.read(path.read_bytes())
    variants = {}
    for group in ("ItemArray", "EquipmentArray", "OcarinaArray"):
        for cell in layout[group]:
            for actor in cell["Actor"]:
                variants.setdefault(actor["ActorShort"], []).append(actor)
    data = tomllib.loads(CATALOG.read_text(encoding="utf-8"))
    for age, items in data.items():
        other = "adult" if age == "child" else "child"
        for item, actor in items.items():
            assert actor in variants, (item, actor)
            for variant in variants[actor]:
                assert variant.get(f"IsUsable{age.title()}", False), (item, variant)
                assert not variant.get(f"IsUsable{other.title()}", False), (item, variant)
