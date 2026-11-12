"""Played named-key opening contracts, shared by native fill eligibility and event compilation."""

SMALL_CHESTS = frozenset({"Obj_TBox_A_01", "Obj_TBox_A_06", "Obj_TBox_GlassTruth_A_01"})
BIG_CHESTS = frozenset({"Obj_TBox_A_02", "Obj_TBox_A_03"})


def source_for(chest: str, kept_event: str | None = None) -> str | None:
    """Kept source events retain their own lifecycle; other kinds need a played default opening."""
    if kept_event is not None:
        return kept_event
    kind = chest.removesuffix("_NoBake")
    if kind in SMALL_CHESTS:
        return "Dm_SY_TreasureboxSmall"
    if kind in BIG_CHESTS:
        return "Dm_SY_Treasurebox"
    return None
