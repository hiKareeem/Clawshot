"""Native progressive grant chains (Round 14, plans/03-game-data.md section 47).

Actor names are acquisition actors; ``owned`` names the saved canonical pouch
identity. Capacity numbers alone are not ownership. No game resource bytes.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tier:
    item: str
    actor: str
    owned: str


CHAINS: dict[str, tuple[Tier, ...]] = {
    "Progressive Hookshot": (
        Tier("Hookshot", "Item_Hookshot", "Item_Hookshot"),
        Tier("Longshot", "Item_Longshot", "Item_Longshot"),
    ),
    "Progressive Strength": (
        Tier("Goron Bracelet", "Item_Gauntlet_Goron", "Armor_Child_Gauntlet_Goron"),
        Tier("Silver Gauntlets", "Item_Gauntlet_Silver", "Armor_Adult_Gauntlet_Silver"),
        Tier("Golden Gauntlets", "Item_Gauntlet_Gold", "Armor_Adult_Gauntlet_Gold"),
    ),
    "Progressive Scale": (
        Tier("Silver Scale", "Item_Scale_Silver", "Item_Scale_Silver"),
        Tier("Golden Scale", "Item_Scale_Gold", "Item_Scale_Gold"),
    ),
    # The native 200-rupee small wallet is starting equipment, not a shuffled upgrade.
    "Progressive Wallet": (
        Tier("Adult Wallet", "Item_Wallet_Medium", "Item_Wallet_Medium"),
        Tier("Giant Wallet", "Item_Wallet_Large", "Item_Wallet_Large"),
    ),
    "Progressive Bomb Bag": (
        Tier("Bomb Bag", "Item_BombBag_Small", "Item_BombBag_Small"),
        Tier("Bomb Bag (30)", "Item_BombBag_Medium", "Item_BombBag_Medium"),
        Tier("Bomb Bag (40)", "Item_BombBag_Large", "Item_BombBag_Large"),
    ),
    # A capacity upgrade alone is not weapon ownership; always establish the weapon first.
    "Progressive Quiver": (
        Tier("Bow", "Item_Range_Bow", "Weapon_Range_Bow"),
        Tier("Quiver (40)", "Item_Quiver_Medium", "Item_Quiver_Medium"),
        Tier("Quiver (50)", "Item_Quiver_Large", "Item_Quiver_Large"),
    ),
    "Progressive Slingshot": (
        Tier("Slingshot", "Item_Range_SlingShot", "Weapon_Range_SlingShot"),
        Tier("Bullet Bag (40)", "Item_BulletBag_Medium", "Item_BulletBag_Medium"),
        Tier("Bullet Bag (50)", "Item_BulletBag_Large", "Item_BulletBag_Large"),
    ),
    "Progressive Magic": (
        Tier("Magic Meter (Single)", "Item_FairyBless_MP", "Item_FairyBless_MP"),
        Tier("Magic Meter (Double)", "Item_FairyBless_MPDouble", "Item_FairyBless_MPDouble"),
    ),
}

FAMILY_BY_ITEM = {tier.item: family for family, tiers in CHAINS.items() for tier in tiers}

# Ownership-dependent native capacity prizes. Unshuffled sources give Medium,
# or Large when Medium is held; shuffled sources are specialized to their fixed
# assignment. Native flow evidence: remake/child_market.toml and section 47.
TIERED_GIFTS = {
    "Market Bombchu Bowling First Prize": ("Bomb Bag (30)", {"Item_BombBag_Medium", "Item_BombBag_Large"}),
    "Market Shooting Gallery Reward": ("Bullet Bag (40)", {"Item_BulletBag_Medium", "Item_BulletBag_Large"}),
    "Kak Shooting Gallery Reward": ("Quiver (40)", {"Item_Quiver_Medium", "Item_Quiver_Large"}),
    "LW Target in Woods": ("Bullet Bag (40)", {"Item_BulletBag_Medium", "Item_BulletBag_Large"}),
    "GF HBA 1500 Points": ("Quiver (40)", {"Item_Quiver_Medium", "Item_Quiver_Large"}),
    "GC Rolling Goron as Child": ("Bomb Bag (30)", {"Item_BombBag_Medium", "Item_BombBag_Large"}),
}


# Native MPMaxUP 24 sources (remake.toml item facts, PouchActorInfo), not extra
# progressive copies. They establish a magic-capacity floor without the MP item.
MAGIC_SOURCES = {
    "Dins Fire": "Item_DinFire",
    "Farores Wind": "Item_FaroreWind",
    "Nayrus Love": "Item_NayruLove",
    "Lens of Truth": "Item_GlassTruth",
    "Fire Arrows": "Item_Arrow_Fire",
    "Ice Arrows": "Item_Arrow_Ice",
    "Light Arrows": "Item_Arrow_Light",
}


def next_tier(family: str, owned: set[str]) -> Tier:
    """The next native grant, capped; separate child/weapon ownership comes first."""
    tiers = CHAINS[family]
    if family == "Progressive Magic" and owned.intersection(MAGIC_SOURCES.values()):
        return tiers[-1]
    if family in {"Progressive Strength", "Progressive Quiver", "Progressive Slingshot"}:
        if tiers[0].owned not in owned:
            return tiers[0]
    for index in range(len(tiers) - 1, -1, -1):
        if tiers[index].owned in owned:
            return tiers[min(index + 1, len(tiers) - 1)]
    return tiers[0]
