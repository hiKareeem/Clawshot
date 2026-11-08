"""Shop definitions are metadata only; the oracle is the player's read-only dump."""

import pytest

from clawshot.census.scan import scan
from clawshot.patch import shops

pytestmark = pytest.mark.dump


def test_every_shop_shelf_matches_its_seller_and_price(romfs):
    slots = shops.load()
    census = {location.id: location for location in scan(romfs) if location.kind == "shop_slot"}
    assert {slot.id for slot in slots} == set(census)
    for slot in slots:
        assert census[slot.id].files == (slot.file,)
    shops.validate(romfs, slots)
    print(f"Validated {len(slots)} shelves in {len({slot.shop for slot in slots})} shops, including mask loans")
