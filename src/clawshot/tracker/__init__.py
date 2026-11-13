"""The item and check tracker, headless: a seed's output plus one of its saves -> what the player holds.

    seed = load_seed("C:/Users/me/Documents/Clawshot/seed-12345")   # UI root, seed pack or raw output
    state = build_state(seed, clawshot.save.load(path))               # JSON-able, spoiler-free by default

    session = TrackerSession()
    session.configure(seed_path, save_folder=None, slot=None, show_locations=False)   # -> snapshot dict
    session.snapshot()                                                               # re-reads only on change

No UI code and no writes: saves and seeds are only read (``plans/00-roadmap.md`` round 14, track A; D38).
"""

from clawshot.tracker.saves import TrackerSession, choose_slot, list_slots, read_complete
from clawshot.tracker.seeds import Check, Place, Seed, SeedError, load_seed, location_index
from clawshot.tracker.state import build_state, collected

__all__ = [
    "Check",
    "Place",
    "Seed",
    "SeedError",
    "TrackerSession",
    "build_state",
    "choose_slot",
    "collected",
    "list_slots",
    "load_seed",
    "location_index",
    "read_complete",
]
