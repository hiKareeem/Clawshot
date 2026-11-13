"""D39: the Gerudo captain keeps the Membership Card in every seed (plans/decisions.md D39).

Owning the card must coincide with the captain's native hand-over, which advances Spirit Step02 and so clears the
guards; a moved card does neither (plans/rounds/r13-gerudo-card.md). No dump: selection runs the generation
pipeline's dump-free steps on the real world, and seeds are filled in a tiny world around the real captain check.
"""

from collections import Counter
from dataclasses import replace

import pytest

from clawshot.app import presets, validate
from clawshot.census import definitions
from clawshot.census.gifts import Gift
from clawshot.generate import FillError, Settings, generate, prepare
from clawshot.generate.fill import check_beatable, shuffled_locations
from clawshot.patch import gifts
from clawshot.patch import items as item_actors
from clawshot.patch.gifts import GiftPatchError
from clawshot.world.load import load_spec
from clawshot.world.model import World

CARD = "Hideout Gerudo Membership Card"
CARD_ITEM = "Gerudo Membership Card"
# The captain's native grant, Dm_Gerudo_0025/Event294, calls this wrapper (r13-gerudo-card.md section 2).
CAPTAIN_CALL = "Dm_SY_GetInEvent:GetInEvent_NotLookatObjectTurnOff"
# A changeable NPC gift for contrast: the Skulltula House's Stone of Agony (03-game-data.md, gift wrappers).
CONTROL = "Kak 20 Gold Skulltula Reward"
CONTROL_CALL = "GatheringTokenGold:TakenReward_Common_Event"


def seed_world(settings: Settings) -> tuple[Settings, World]:
    """The settings and world a seed fills, through the dump-free steps of generation (app.jobs or the CLI, then
    gifts.seed_setup, then make_seed's prepare). Without the dump's census every world gift of a shuffled type stays
    movable, an upper bound on gifts.seed_checks: only the world's own metadata can hold the captain."""
    spec = load_spec()
    if gifts.SHUFFLE in settings.shuffle or set(settings.shuffle) & set(gifts.GIFT_TYPES):
        kinds = (kind for s in settings.shuffle for kind in (gifts.GIFT_TYPES if s == gifts.SHUFFLE else (s,)))
        settings = replace(settings, shuffle=tuple(kinds))
        if "NPC" in settings.shuffle:
            spec = gifts.shopkeeper_spec(spec)
    return prepare(spec, settings)


def assert_card_held(settings: Settings, label: str) -> None:
    """The captain is not selected and the card is not in the pool: it stays exactly once, at the captain."""
    effective, world = seed_world(settings)
    shuffled = shuffled_locations(world, effective)
    pool = Counter(world.locations[name].vanilla for name in shuffled)
    fixed = [name for name, loc in world.locations.items() if name not in shuffled and loc.vanilla == CARD_ITEM]
    assert CARD not in shuffled, label
    assert pool[CARD_ITEM] == 0, label
    assert fixed == [CARD], label


def test_no_ui_preset_selects_the_captain():
    # Each preset as the generation job decodes it: from its shared settings string.
    for preset in presets():
        assert_card_held(validate(text=preset["settings_string"]), preset["id"])


@pytest.mark.parametrize(
    "choice",
    [
        pytest.param({"shuffle": ["Gift"]}, id="ui-gift"),
        pytest.param(
            {"shuffle": ["Chest", "Gift"], "songs": "anywhere", "dungeon_items": "anywhere"},
            id="ui-gift-songs-and-keys-anywhere",
        ),
        # Expanded kinds, as an effective spoiler string replays them through the CLI (the UI offers only Gift).
        pytest.param(Settings(shuffle=("NPC",)), id="npc-only"),
        pytest.param(Settings(shuffle=("Chest", *gifts.GIFT_TYPES), songs="anywhere"), id="every-gift-type"),
    ],
)
def test_no_gift_setting_selects_the_captain(choice):
    settings = validate(choice) if isinstance(choice, dict) else choice
    assert_card_held(settings, repr(choice))


def census_step(check: str, call: str, param: str) -> Gift:
    """A check's native grant as the dump's gift census reports it: id, flow, event and item from its definition
    (data/locations.toml), with its documented wrapper call; selection and planning read no other field."""
    definition = next(d for d in definitions.load() if d.oot_randomizer_name == check)
    flow, event = definition.id.split("/")
    return Gift(definition.id, definition.kind, flow, "", (), event, call, param, definition.vanilla_item, "")


def test_gift_selection_and_the_gift_patch_refuse_the_captains_grant():
    _, world = seed_world(Settings(shuffle=(gifts.SHUFFLE,)))
    captain = census_step(CARD, CAPTAIN_CALL, "ActorName")
    control = census_step(CONTROL, CONTROL_CALL, "TakenRewardActor")
    census, defs, rules, actors = [captain, control], definitions.load(), gifts.load(), item_actors.load()
    assert gifts.seed_checks(world, census, defs, rules, actors) == [CONTROL]
    # Nor can a placement handed straight to the gift patch rewrite the captain's hand-over.
    with pytest.raises(GiftPatchError):
        gifts.plan({CARD: control.vanilla_item}, [captain], defs, rules)


def check(kind: str, vanilla: str) -> dict:
    return {"rule": "True", "type": kind, "vanilla": vanilla}


def fortress_world() -> dict:
    """The real captain check (its production location metadata and item) in a tiny world: the shuffled Hookshot
    frees the carpenters, the captain hands over the card, and only the card opens the fortress whose clearance
    (with the shuffled Bow) is the goal."""
    real = load_spec()
    return {
        "start": "Valley",
        "goal": "'Fortress Cleared'",
        "items": {CARD_ITEM: real["items"][CARD_ITEM], "Hookshot": {}, "Bow": {}, "Rupees (5)": {"class": "normal"}},
        "locations": {CARD: real["locations"][CARD]},
        "regions": [
            {
                "name": "Valley",
                "locations": {"Valley Chest": check("Chest", "Hookshot"), "Valley Gift": check("NPC", "Rupees (5)")},
                "exits": {"Hideout": "Hookshot"},
            },
            {
                "name": "Hideout",
                "locations": {CARD: "True", "Hideout Chest": check("Chest", "Rupees (5)")},
                "exits": {"Fortress": "Gerudo_Membership_Card"},
            },
            {
                "name": "Fortress",
                "locations": {"Fortress Chest": check("Chest", "Bow"), "Fortress Gift": check("NPC", "Rupees (5)")},
                "events": {"Fortress Cleared": "Bow"},
            },
        ],
    }


def test_seeds_fill_around_the_vanilla_captain_and_need_its_card():
    spec = fortress_world()
    others = ["Valley Chest", "Valley Gift", "Hideout Chest", "Fortress Chest", "Fortress Gift"]
    for number in range(20):
        seed = generate(spec, number, Settings(shuffle=("Chest", *gifts.GIFT_TYPES)))
        # Every other check, the NPC gifts too, is shuffled; the captain is not, and the card is nowhere else.
        assert seed.shuffled == others, number
        assert [name for name, item in seed.placements.items() if item == CARD_ITEM] == [CARD], number
        sphere = {name: i for i, names in enumerate(seed.spheres) for name in names}
        hookshot = next(name for name, item in seed.placements.items() if item == "Hookshot")
        assert sphere[hookshot] < sphere[CARD] < min(sphere["Fortress Chest"], sphere["Fortress Gift"]), number
        # The native hand-over is what wins: without the captain's card the goal cannot be reached.
        without = {name: item for name, item in seed.placements.items() if name != CARD}
        with pytest.raises(FillError):
            check_beatable(seed.world, without)
