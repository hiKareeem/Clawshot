"""Round 14 progressive logic (issue #13, plans/03-game-data.md section 47): a seed's world counts only progressive
copies, the Nth copy tier N, and each chain it gives gets its full set of copies, so an unshuffled native reward is a
bonus in any order of play. Synthetic worlds, plus the repository's own world data (no game data)."""

import random
from collections import Counter
from itertools import permutations

import pytest

from clawshot.generate import prepare
from clawshot.generate.fill import (
    FillError,
    Settings,
    _age_family,
    _swap,
    allowed,
    check_beatable,
    fill,
    shuffled_locations,
)
from clawshot.generate.progressive import normalize_pool, prepare_spec, restrict_settings
from clawshot.progressive import CHAINS, FAMILY_BY_ITEM
from clawshot.world import ADULT, CHILD, Search, WorldError, build_world, load_spec
from clawshot.world.rules import DAY

STRENGTH = "Progressive Strength Upgrade"
COPY = "Progressive Strength"
HOOK = "Progressive Hookshot"
MAGIC = "Progressive Magic"
ITEMS = {
    HOOK: {},
    STRENGTH: {},
    COPY: {"alias": [STRENGTH, 1]},
    "Magic Meter": {},
    MAGIC: {"alias": ["Magic Meter", 1]},
    "Dins Fire": {"alias": ["Magic Meter", 1]},
    "Farores Wind": {"alias": ["Magic Meter", 1]},
    "Rupees (5)": {"class": "normal"},
    "Deku Nuts (5)": {"class": "normal"},
    "Buy Arrows (10)": {"type": "Shop", "class": "priority"},
}
PROGRESSIVE = {
    HOOK: ["Hookshot", "Longshot"],
    STRENGTH: ["Goron Bracelet", "Silver Gauntlets", "Golden Gauntlets"],
    "Magic Meter": ["Magic Meter (Single)", "Magic Meter (Double)"],
}
DIRECT = {"chains": [HOOK, COPY, MAGIC], "first": [COPY], "destinations": ["Chest"]}
"""Native chains in a world built directly: fixed tiers still count (the oracle's compatibility)."""
SEED = {**DIRECT, "copies_only": True}
"""The same chains as a seed's world sees them (``prepare_spec`` sets ``copies_only``)."""


def spec(regions: list[dict], *, goal: str = "True", settings: dict | None = None, native: dict = SEED) -> dict:
    return {
        "start": "Root",
        "goal": goal,
        "items": ITEMS,
        "progressive": PROGRESSIVE,
        "native_progressive": native,
        "settings": {"progressive_items": False, **(settings or {})},
        "regions": regions,
    }


def chest(vanilla: str, rule: str = "True") -> dict:
    return {"rule": rule, "type": "Chest", "vanilla": vanilla}


def counts_after(*items: str, native: dict = SEED) -> dict[str, int]:
    search = Search(build_world(spec([{"name": "Root"}], native=native)))
    for item in items:
        search.collect(item)
    return search.counts


@pytest.mark.parametrize(
    ("items", "family", "level"),
    [
        ((HOOK,), HOOK, 1),
        ((HOOK,) * 2, HOOK, 2),
        ((COPY,), STRENGTH, 1),
        ((COPY,) * 2, STRENGTH, 2),
        ((COPY,) * 3, STRENGTH, 3),
        ((MAGIC,) * 2, "Magic Meter", 2),
    ],
)
def test_the_nth_copy_is_tier_n(items, family, level):
    counts = counts_after(*items)
    assert counts[family] == level
    assert all(counts[item] == items.count(item) for item in items if item != family)  # raw copies stay counted


@pytest.mark.parametrize(
    ("items", "family", "level"),
    [
        (("Goron Bracelet", "Silver Gauntlets", "Golden Gauntlets"), STRENGTH, 0),
        (("Golden Gauntlets", COPY), STRENGTH, 1),
        (("Longshot", HOOK), HOOK, 1),
        (("Magic Meter (Double)",), "Magic Meter", 0),
        # A spell is still the spell; the meter it opens is a bonus like a fixed tier.
        (("Dins Fire", "Farores Wind"), "Magic Meter", 0),
        (("Magic Meter (Single)", "Dins Fire", MAGIC), "Magic Meter", 1),
    ],
)
def test_a_seed_world_counts_only_copies(items, family, level):
    counts = counts_after(*items)
    assert counts.get(family, 0) == level
    assert all(counts[item] == 1 for item in items if item not in (COPY, HOOK, MAGIC))  # their own names still count


@pytest.mark.parametrize("order", sorted(set(permutations(("Goron Bracelet", COPY, COPY, COPY)))))
def test_the_native_bracelet_never_changes_the_count_in_any_order(order):
    # Darunia first: the copies give the Silver and Golden Gauntlets, the third a harmless leftover. Copies first:
    # the Bracelet, Silver and Golden Gauntlets, then the gift repeats the Bracelet. The logic assumes neither.
    assert counts_after(*order)[STRENGTH] == 3
    assert counts_after(*order[:-1])[STRENGTH] == order[:-1].count(COPY)


@pytest.mark.parametrize("order", sorted(set(permutations(("Magic Meter (Double)", "Dins Fire", MAGIC, MAGIC)))))
def test_native_magic_never_changes_the_count_in_any_order(order):
    assert counts_after(*order)["Magic Meter"] == 2


def test_a_world_built_directly_keeps_fixed_tiers():
    assert counts_after("Goron Bracelet", "Silver Gauntlets", native=DIRECT)[STRENGTH] == 2  # a floor, never a sum
    assert counts_after("Longshot", native=DIRECT)[HOOK] == 2
    direct = build_world(spec([{"name": "Root"}], native=DIRECT))
    seed = build_world(spec([{"name": "Root"}]))
    assert not direct.progressive_copies_only and seed.progressive_copies_only
    assert direct.items["Silver Gauntlets"].tier and not seed.items["Silver Gauntlets"].tier
    assert seed.items[COPY].alias == (STRENGTH, 1)  # the copy's own alias stays
    with pytest.raises(WorldError, match="copies_only"):
        build_world(spec([{"name": "Root"}], native={**DIRECT, "copies_only": "yes"}))


@pytest.mark.parametrize("copies", range(4))
def test_seed_child_strength_requires_native_darunia_source_without_counting_it_as_a_copy(copies):
    real = load_spec()
    _, world = prepare({**real, "start": "Goron City", "goal": "Bombs"}, Settings())
    search = Search.child_only(
        world, ["Fairy Ocarina", "Zeldas Lullaby", "Sarias Song", "Progressive Bomb Bag", *([COPY] * copies)]
    )
    gift = world.locations["GC Darunias Joy"]
    # His door/song route is available without first opening the DC boulder.
    assert search.can_access(gift, CHILD)
    assert not search.can_reach("Dodongos Cavern Beginning", CHILD)
    assert not world.goal(search.counts, CHILD, DAY)
    search.collect_spheres({gift.name: gift.vanilla})
    assert gift.name in search.collected
    assert search.can_reach("Dodongos Cavern Beginning", CHILD)
    assert world.goal(search.counts, CHILD, DAY)
    assert search.counts.get(STRENGTH, 0) == copies
    assert world.goal(search.counts, ADULT, DAY) is (copies > 0)


@pytest.mark.parametrize("missing", ["Zeldas Lullaby", "Sarias Song"])
def test_even_three_copies_cannot_bypass_darunias_door_or_song_in_child_logic(missing):
    real = load_spec()
    _, world = prepare({**real, "start": "Goron City", "goal": "Bombs"}, Settings())
    items = ["Fairy Ocarina", "Zeldas Lullaby", "Sarias Song", "Progressive Bomb Bag", COPY, COPY, COPY]
    items.remove(missing)
    search = Search.child_only(world, items)
    assert not search.can_access(world.locations["GC Darunias Joy"], CHILD)
    assert not search.can_reach("Dodongos Cavern Beginning", CHILD)
    assert not world.goal(search.counts, CHILD, DAY)


def gated_world(*, return_opens: bool):
    """Child's rock needs the child Bracelet; adult's chest is out of child's reach until the return opens. Built
    directly, so the fixed gauntlets raise the logical strength level."""
    child_strength = "('Goron Bracelet' or Progressive_Strength)"
    return build_world(
        spec(
            [
                {"name": "Root", "exits": {"Field": "age == starting_age or 'Time Travel'"}},
                {
                    "name": "Field",
                    "exits": {"Temple": "True"},
                    "locations": {
                        "Adult Chest": {"rule": "age == 'adult'", "type": "Chest"},
                        "Child Rock": {"rule": f"age == 'child' and {child_strength}", "type": "Chest"},
                    },
                    "events": {"Forest Clear": "age == 'adult' and " + ("True" if return_opens else "False")},
                },
                {"name": "Temple", "events": {"Time Travel": "True"}},
            ],
            settings={"starting_age": "child", "age_return_event": "Forest Clear", "age_return_region": "Temple"},
            native=DIRECT,
        )
    )


def test_adult_gauntlets_never_give_child_the_bracelet_across_the_return():
    search = Search(gated_world(return_opens=True))
    search.collect_spheres({"Adult Chest": "Silver Gauntlets", "Child Rock": "Rupees (5)"})
    assert search.counts[STRENGTH] == 2
    assert not search.can_access(search.world.locations["Child Rock"], CHILD)


def test_a_raw_copy_is_child_strength_once_the_return_shares_it():
    placements = {"Adult Chest": COPY, "Child Rock": "Rupees (5)"}
    closed = Search(gated_world(return_opens=False))
    closed.collect_spheres(placements)
    assert closed.counts[COPY] == 1 and closed.counts[STRENGTH] == 1
    assert closed._child_counts.get(COPY, 0) == 0  # the child's pre-return view stays isolated
    assert "Child Rock" not in closed.collected
    opened = Search(gated_world(return_opens=True))
    opened.collect_spheres(placements)
    assert "Child Rock" in opened.collected
    assert opened.can_access(opened.world.locations["Child Rock"], CHILD)


@pytest.fixture(scope="module")
def native_spec():
    return prepare_spec(load_spec())


@pytest.fixture(scope="module")
def native_world(native_spec):
    return build_world(native_spec)


def test_seeds_count_only_copies_and_cannot_switch_to_legacy_progressive_items(native_spec, native_world):
    assert native_spec["native_progressive"]["copies_only"] and native_world.progressive_copies_only
    assert not build_world(load_spec()).progressive_copies_only  # the directly built oracle keeps fixed tiers
    for value in (True, False):
        with pytest.raises(WorldError, match="progressive_items"):
            build_world(native_spec, {"progressive_items": value})
    with pytest.raises(WorldError, match="progressive_copies_only"):
        build_world(native_spec, {"progressive_copies_only": False})
    custom = spec([{"name": "Root"}], native={})
    assert prepare_spec(custom) is custom  # a world without native chains is not touched
    with pytest.raises(WorldError, match="catalog"):
        prepare_spec(spec([{"name": "Root"}]))  # declared chains must be the catalog's eight


def test_the_default_pool_holds_every_chain_in_full(native_world):
    settings = Settings()
    overrides = normalize_pool(native_world, settings)
    assert Counter(overrides.values()) == {family: len(tiers) for family, tiers in CHAINS.items()}
    assert len(overrides) == 20
    world_vanilla = {name: location.vanilla for name, location in native_world.locations.items()}
    sources = [name for name in overrides if world_vanilla[name] in FAMILY_BY_ITEM]
    assert len(sources) == 7  # the shuffled chests' own upgrades
    assert overrides["Water Temple Longshot Chest"] == HOOK
    assert overrides["Forest Temple Bow Chest"] == "Progressive Quiver"
    # The 13 missing copies replace the first chest rupees in world order.
    rupees = [
        name
        for name in shuffled_locations(native_world, settings)
        if native_world.locations[name].type == "Chest" and world_vanilla[name].startswith("Rupee")
    ]
    assert [name for name in overrides if name not in sources] == rupees[:13]
    assert normalize_pool(native_world, settings) == overrides
    # Unshuffled native rewards keep their fixed tier: bonuses beside the full chains.
    assert "GC Darunias Joy" not in overrides
    assert world_vanilla["GC Darunias Joy"] == "Goron Bracelet"
    assert world_vanilla["GF HBA 1500 Points"] == "Quiver (40)"  # a quiver upgrade, never a free Bow
    assert world_vanilla["GC Rolling Goron as Child"] == "Bomb Bag (30)"
    assert world_vanilla["HC Great Fairy Reward"] == "Magic Meter (Single)"
    assert world_vanilla["DMC Great Fairy Reward"] == "Magic Meter (Double)"


@pytest.mark.parametrize("family", sorted(CHAINS))
def test_every_native_chain_counts_only_its_copies(native_world, family):
    logic = native_world.progressive[family]
    tiers = [tier.item for tier in CHAINS[family]]
    fixed = Search(native_world, tiers)
    assert fixed.counts.get(logic, 0) == 0
    for n in range(1, len(tiers) + 1):
        copies = Search(native_world, [family] * n)
        assert copies.counts[logic] == n
        for item in tiers:
            copies.collect(item)
        assert copies.counts[logic] == n


def test_spells_keep_their_names_but_open_no_meter(native_world):
    spells = Search(native_world, ["Dins Fire", "Lens of Truth", "Fire Arrows"])
    assert spells.counts.get("Magic Meter", 0) == 0
    assert spells.counts["Dins Fire"] == 1
    assert Search(native_world, ["Dins Fire", MAGIC]).counts["Magic Meter"] == 1


def test_capacity_upgrades_are_never_the_weapon(native_world):
    held = Search(native_world, ["Quiver (40)", "Quiver (50)", "Bullet Bag (40)", "Bullet Bag (50)", "Bomb Bag (30)"])
    assert held.counts.get("Bow", 0) == 0
    assert held.counts.get("Slingshot", 0) == 0
    assert held.counts.get("Bomb Bag", 0) == 0
    copies = Search(native_world, ["Progressive Quiver", "Progressive Slingshot", "Progressive Bomb Bag"])
    assert copies.counts["Bow"] == 1  # the first copy of each is the weapon itself
    assert copies.counts["Slingshot"] == 1
    assert copies.counts["Bomb Bag"] == 1


def test_raw_families_keep_their_logical_families(native_world):
    families = {item: _age_family(native_world, item) for item in CHAINS}
    assert families == {
        HOOK: HOOK,
        COPY: STRENGTH,  # the return kit's strength family and its adult-only bypass
        "Progressive Scale": "Progressive Scale",
        "Progressive Wallet": "Progressive Wallet",
        "Progressive Bomb Bag": "Bomb Bag",  # a D25 bag source: never a pack's first bag
        "Progressive Quiver": "Bow",
        "Progressive Slingshot": "Slingshot",
        MAGIC: "Magic Meter",
    }
    assert all(native_world.items[item].progression for item in CHAINS)  # hints and fill treat copies as major


def test_restrict_settings_holds_copies_to_chests(native_world):
    held = restrict_settings(native_world, Settings()).item_location_types
    assert {item: held[item] for item in CHAINS} == dict.fromkeys(CHAINS, ("Chest",))
    narrowed = restrict_settings(native_world, Settings(item_location_types={"Progressive Scale": ["Chest", "NPC"]}))
    assert narrowed.item_location_types["Progressive Scale"] == ("Chest",)
    with pytest.raises(FillError, match="Progressive Scale"):
        restrict_settings(native_world, Settings(item_location_types={"Progressive Scale": ["NPC"]}))
    custom = build_world(spec([{"name": "Root"}], native={}))
    settings = Settings()
    assert restrict_settings(custom, settings) is settings


def donor_world():
    """A Hookshot chest, a fixed double-meter fairy and assorted chest contents; no strength source anywhere."""
    locations = {
        "Hook Chest": chest("Hookshot"),
        "Magic Fairy": {"rule": "True", "type": "Cutscene", "vanilla": "Magic Meter (Double)"},
        "Nuts Chest": chest("Deku Nuts (5)"),
        "Spell Chest": chest("Dins Fire"),
        "Shop Chest": chest("Buy Arrows (10)"),
        "Rupee Gift": {"rule": "True", "type": "NPC", "vanilla": "Rupees (5)"},
        "Rupee Chest A": chest("Rupees (5)"),
        "Rupee Chest B": chest("Rupees (5)"),
    }
    return build_world(spec([{"name": "Root", "locations": locations}]))


def test_missing_copies_replace_ordinary_chest_filler_rupees_first():
    world = donor_world()
    settings = Settings(shuffle=("Chest", "NPC"))
    assert normalize_pool(world, settings) == {
        "Hook Chest": HOOK,
        "Rupee Chest A": HOOK,
        "Rupee Chest B": MAGIC,
        "Nuts Chest": MAGIC,  # the unshuffled fairy keeps its double meter as a bonus; no strength copy at all
    }
    with pytest.raises(FillError, match="3 more copies .* has 2"):
        normalize_pool(world, settings, {"Nuts Chest": "Dins Fire"})  # never a progression, shop or NPC slot
    with pytest.raises(FillError, match="shuffle"):
        normalize_pool(world, Settings(shuffle=("NPC",)))  # copies go only to chests, so chests must shuffle


def strength_world(*, prize: bool = False, win: int = 3, gift: str = "True"):
    """The rock needs strength, the boulder the Silver Gauntlets, the win level ``win``. The Bracelet is Darunia's gift
    (NPC, reached by ``gift``); with ``prize`` it is a fixed cutscene reward instead and a minigame (NPC) gives the
    Golden Gauntlets."""
    locations = {
        "Gift": {"rule": gift, "type": "Cutscene" if prize else "NPC", "vanilla": "Goron Bracelet"},
        "Open A": chest("Rupees (5)"),
        "Open B": chest("Rupees (5)"),
        "Rock Chest": chest("Silver Gauntlets", "Progressive_Strength_Upgrade"),
        "Boulder Chest": chest("Rupees (5)" if prize else "Golden Gauntlets", "(Progressive_Strength_Upgrade, 2)"),
    }
    if prize:
        locations["Prize"] = {"rule": "True", "type": "NPC", "vanilla": "Golden Gauntlets"}
    events = {"Win": f"(Progressive_Strength_Upgrade, {win})"}
    return build_world(spec([{"name": "Root", "locations": locations, "events": events}], goal="'Win'"))


def seeded(world, shuffle: tuple[str, ...], seed: int) -> tuple[Settings, dict[str, str]]:
    settings = restrict_settings(world, Settings(shuffle=shuffle))
    return settings, fill(world, settings, random.Random(seed), normalize_pool(world, settings))


def test_a_shuffled_gift_completes_its_chain_as_copies():
    world = strength_world()
    settings = restrict_settings(world, Settings(shuffle=("Chest", "NPC")))
    vanilla = normalize_pool(world, settings)
    assert vanilla == {"Gift": COPY, "Rock Chest": COPY, "Boulder Chest": COPY}  # the gift's own Bracelet too
    for seed in range(5):
        placements = fill(world, settings, random.Random(seed), vanilla)
        assert Counter(placements.values())[COPY] == 3
        assert all(world.locations[name].type == "Chest" for name, item in placements.items() if item == COPY)
        check_beatable(world, placements)  # three copies are the Golden Gauntlets, whatever the order


@pytest.mark.parametrize("gift", ["True", "False"])
def test_an_unshuffled_gift_is_a_bonus_beside_a_full_chain(gift):
    world = strength_world(gift=gift)
    settings = restrict_settings(world, Settings(shuffle=("Chest",)))
    vanilla = normalize_pool(world, settings)
    assert vanilla == {"Rock Chest": COPY, "Boulder Chest": COPY, "Open A": COPY}  # filler makes the third copy
    for seed in range(5):
        placements = fill(world, settings, random.Random(seed), vanilla)
        assert placements["Gift"] == "Goron Bracelet"
        check_beatable(world, placements)  # the Golden Gauntlets need no native gift, reachable or not
    assert normalize_pool(world, Settings(shuffle=("Chest",)), {"Open A": "Silver Gauntlets"}) == {
        "Open A": COPY,
        "Rock Chest": COPY,
        "Boulder Chest": COPY,
    }


def test_copies_never_take_an_unsupported_check_through_fill_or_swap():
    world = strength_world(prize=True, win=2)
    settings, placements = seeded(world, ("Chest", "NPC"), 3)
    assert placements["Gift"] == "Goron Bracelet"
    copies = [name for name, item in placements.items() if item == COPY]
    assert len(copies) == 3  # the prize's own and a filler chest's, beside the Silver Gauntlets chest's
    assert all(world.locations[name].type == "Chest" for name in copies)
    assert placements["Prize"] == "Rupees (5)"
    check_beatable(world, placements)
    for checked in (settings, Settings(shuffle=("Chest", "NPC"))):  # held by the settings, and by the world itself
        assert not allowed(world, checked, "Prize", COPY)
    filled = {"Gift": "Goron Bracelet", "Prize": "Rupees (5)", "Open A": "Rupees (5)"}
    assert _swap(world, settings, filled, ["Prize", "Open A"], COPY, [COPY], {}) == "Open A"


def test_the_same_seed_replays_the_same_progressive_fill():
    world = strength_world(prize=True, win=2)
    assert seeded(world, ("Chest", "NPC"), 11)[1] == seeded(world, ("Chest", "NPC"), 11)[1]
