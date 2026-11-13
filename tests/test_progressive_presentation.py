"""Progressive copies keep their family label; the spoiler adds route-dependent tiers from one canonical replay."""

import json
from dataclasses import replace

import pytest

from clawshot.generate import Seed, Settings, play_note, spoiler
from clawshot.generate.hints import Hint
from clawshot.generate.itembar import age_locked_pickups
from clawshot.patch import text
from clawshot.patch.items import ItemActors
from clawshot.progressive import CHAINS
from clawshot.world import Search, build_world


def seed_of(placements, rules, *, shuffled=None, starting_age="child"):
    """A one-field world collected by the real search; ``shuffled`` defaults to every location."""
    world = build_world(
        {
            "start": "Root",
            "goal": "True",
            "settings": {"starting_age": starting_age},
            "items": {item: {} for item in dict.fromkeys(placements.values())},
            "locations": {name: {"type": "Chest", "vanilla": item} for name, item in placements.items()},
            "regions": [
                {"name": "Root", "exits": {"Field": "age == starting_age or 'Time Travel'"}},
                {"name": "Field", "locations": rules},
            ],
        }
    )
    spheres = Search(world).collect_spheres(placements)
    return Seed(world, 9, Settings(), placements, list(placements) if shuffled is None else shuffled, spheres)


def chained(first, family):
    """``first`` (a fixed native bonus, unshuffled) in sphere 1, then one ``family`` copy each in spheres 2 and 3."""
    placements = {"Native": first, "Coin chest": "Coin", "Copy 1": family, "Key chest": "Key", "Copy 2": family}
    rules = {"Native": "True", "Coin chest": "True", "Copy 1": "Coin", "Key chest": "Coin", "Copy 2": "Key"}
    return seed_of(placements, rules, shuffled=["Coin chest", "Copy 1", "Key chest", "Copy 2"])


def table_rows(note):
    return [
        line.removeprefix("| ").removesuffix(" |").split(" | ") for line in note.splitlines() if line.startswith("| ")
    ]


def test_game_text_names_keep_family_labels_without_reading_any_actor_pack(tmp_path):
    # Even a table that names a base actor for the family must not turn it into that tier's game name. The romfs
    # folder does not exist: no archive or actor pack may be read when no item needs game text.
    table = ItemActors({"Progressive Hookshot": "Item_Hookshot"}, {})
    names = text.item_names(tmp_path / "no-romfs", [*CHAINS, "Coin", "Progressive Hookshot"], table)
    assert names == {family: family for family in sorted(CHAINS)} | {"Coin": "Coin"}


def test_spoiler_hints_and_note_say_the_family_never_the_base_tier():
    placements = {"Chest": "Progressive Hookshot", "Quiver chest": "Progressive Quiver"}
    seed = seed_of(placements, {name: "True" for name in placements})
    hint = Hint("KF Gossip Stone", "GOSSIP_KOKIRI_FOREST_01", "random", location="Chest", item="Progressive Hookshot")
    seed = replace(seed, hints=(hint,))
    # A stale base-tier name for the family (as an actor lookup would give) cannot leak into any output.
    log = json.loads(json.dumps(spoiler(seed, {"Progressive Hookshot": "Hookshot"})))
    assert log["placements"] == placements
    [logged] = log["hints"]
    assert logged["item"] == "Progressive Hookshot"
    assert "Progressive Hookshot" in logged["text"]
    assert "Progressive Hookshot" not in log["item_names"]
    assert log["item_names"]["Bow"] == "Fairy Bow"  # a tier the copy can give is named as the remake names it
    rows = table_rows(play_note(seed, log))
    rewards = {row[3]: row[4] for row in rows if len(row) == 5 and row[3] in seed.shuffled}
    assert rewards == placements
    progressive = {row[2]: row for row in rows if len(row) == 6 and row[2] in seed.shuffled}
    assert progressive["Chest"][3:] == ["Progressive Hookshot", "Hookshot → Longshot", "Hookshot"]
    assert progressive["Quiver chest"][3:5] == ["Progressive Quiver", "Fairy Bow → Quiver (40) → Quiver (50)"]
    stone = next(row for row in rows if row[0] == "KF Gossip Stone")
    assert stone[4] == "Chest — Progressive Hookshot"


def test_canonical_replay_follows_actual_sphere_order_not_location_or_seed():
    placements = {"Gate": "Coin", "Left": "Progressive Hookshot", "Right": "Progressive Hookshot"}
    left_first = seed_of(placements, {"Gate": "True", "Left": "True", "Right": "Coin"})
    right_first = seed_of(placements, {"Gate": "True", "Left": "Coin", "Right": "True"})

    def given(seed):
        grants = spoiler(seed)["progressive_grants"]["locations"].items()
        return {name: (grant["canonical_sphere"], grant["given_in_canonical_sphere_replay"]) for name, grant in grants}

    assert given(left_first) == {"Left": (1, "Hookshot"), "Right": (2, "Longshot")}
    assert given(right_first) == {"Left": (2, "Longshot"), "Right": (1, "Hookshot")}
    # No randomness: another seed number with the same placements and spheres replays identically.
    assert given(replace(left_first, seed=12345)) == given(left_first)
    for name, grant in spoiler(left_first)["progressive_grants"]["locations"].items():
        assert grant["family"] == "Progressive Hookshot"
        assert grant["possible_tiers"] == ["Hookshot", "Longshot"], name


@pytest.mark.parametrize(
    ("native", "family", "expected", "leftover"),
    [
        ("Coin", "Progressive Strength", ["Goron Bracelet", "Silver Gauntlets"], [False, False]),
        ("Goron Bracelet", "Progressive Strength", ["Silver Gauntlets", "Golden Gauntlets"], [False, False]),
        # Adult gauntlets never stand in for child Link's Bracelet.
        ("Silver Gauntlets", "Progressive Strength", ["Goron Bracelet", "Golden Gauntlets"], [False, False]),
        # After a native bonus the chain can be complete: later copies are harmless leftovers, never a downgrade.
        ("Hookshot", "Progressive Hookshot", ["Longshot", "Longshot"], [False, True]),
        ("Longshot", "Progressive Hookshot", ["Longshot", "Longshot"], [True, True]),
        ("Silver Scale", "Progressive Scale", ["Golden Scale", "Golden Scale"], [False, True]),
        ("Adult Wallet", "Progressive Wallet", ["Giant Wallet", "Giant Wallet"], [False, True]),
        ("Bomb Bag (30)", "Progressive Bomb Bag", ["Bomb Bag (40)", "Bomb Bag (40)"], [False, True]),
        # A fixed capacity upgrade is not the weapon: the weapon comes first.
        ("Quiver (40)", "Progressive Quiver", ["Bow", "Quiver (50)"], [False, False]),
        ("Bullet Bag (40)", "Progressive Slingshot", ["Slingshot", "Bullet Bag (50)"], [False, False]),
        # A spell's native meter is a floor, not a copy: the first copy is already the double meter.
        ("Dins Fire", "Progressive Magic", ["Magic Meter (Double)", "Magic Meter (Double)"], [False, True]),
        ("Coin", "Progressive Magic", ["Magic Meter (Single)", "Magic Meter (Double)"], [False, False]),
    ],
)
def test_replay_counts_native_bonuses_and_copies_in_collection_order(native, family, expected, leftover):
    seed = chained(native, family)
    log = spoiler(seed)
    grants = log["progressive_grants"]["locations"]
    assert list(grants) == ["Copy 1", "Copy 2"]  # the fixed reward is a bonus source of ownership, never a copy
    assert [grants[name]["canonical_sphere"] for name in grants] == [2, 3]
    assert [grants[name]["given_in_canonical_sphere_replay"] for name in grants] == expected
    assert [grants[name]["leftover_in_canonical_replay"] for name in grants] == leftover
    assert seed.placements["Native"] == native  # reporting never replaces a reward
    # The note tells a leftover apart from a new tier without renaming the tier it repeats.
    rows = {row[2]: row for row in table_rows(play_note(seed, log)) if len(row) == 6 and row[2] in grants}
    for name, tier, spare in zip(grants, expected, leftover, strict=True):
        tier = log["item_names"].get(tier, tier)
        assert (rows[name][5] != tier, tier in rows[name][5]) == (spare, True), (name, rows[name][5])


def test_a_copy_the_search_never_collects_has_no_canonical_tier():
    seed = seed_of({"Open": "Progressive Scale", "Shut": "Progressive Scale"}, {"Open": "True", "Shut": "False"})
    log = spoiler(seed)
    grants = log["progressive_grants"]["locations"]
    assert grants["Shut"]["canonical_sphere"] is None
    assert grants["Shut"]["given_in_canonical_sphere_replay"] is None
    assert grants["Open"]["given_in_canonical_sphere_replay"] == "Silver Scale"
    row = next(row for row in table_rows(play_note(seed, log)) if len(row) == 6 and row[2] == "Shut")
    assert row[0] == "—" and row[5].startswith("—")


@pytest.mark.parametrize(
    ("family", "starting_age", "usable"),
    [
        ("Progressive Hookshot", "child", "adult"),
        ("Progressive Quiver", "child", "adult"),
        ("Progressive Slingshot", "adult", "child"),
    ],
)
def test_age_locked_base_families_warn_like_their_weapon(family, starting_age, usable):
    seed = seed_of({"Chest": family}, {"Chest": "True"}, starting_age=starting_age)
    [warning] = age_locked_pickups(seed)
    assert (warning.item, warning.usable_age, warning.first_ages) == (family, usable, (starting_age,))
