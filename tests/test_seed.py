"""The committed data the seed writer reads: every item round 3's slice can place in a chest has an actor."""

from clawshot.census.definitions import load as load_definitions
from clawshot.census.scan import CHEST
from clawshot.generate import Settings, prepare
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import items as item_actors
from clawshot.world import load_spec

# Round 3's playtest: Kokiri Forest, the Lost Woods and the Deku Tree, beaten at Queen Gohma.
SLICE = Settings(areas=("KokiriForest", "LostWood", "InsideTheDekuTree"), goal="'Defeat Queen Gohma'")


def test_every_placeable_item_has_an_actor():
    """The pool is what the remake's chests hold at the shuffled locations (locations.toml vanilla_item): each such
    actor reads back as a logic item, and that item's actor is the same actor."""
    _, world = prepare(load_spec(), SLICE)
    table = item_actors.load()
    table.check(world.items)
    named: dict[str, list] = {}
    for d in load_definitions():
        named.setdefault(d.oot_randomizer_name, []).append(d)
    shuffled = shuffled_locations(world, SLICE)
    assert shuffled
    for name in shuffled:
        chests = named.get(name, [])
        assert chests and all(d.kind == CHEST for d in chests), name
        dungeon = world.regions[world.locations[name].region].dungeon
        for d in chests:
            item = table.item(d.vanilla_item, dungeon, world.items)
            assert table.actor(item) == d.vanilla_item, (name, item)
