"""Dungeons whose small keys can be granted by name: the logic dungeon, its native save struct and its name label.

A generic small key credits the dungeon Link stands in (``RSDB/DungeonParam``'s row for the loaded Banc area, whose
``TargetGameData`` selects one ``GameData`` ``DungeonInfo`` struct) and is lost in the overworld. A key found
outside its own dungeon therefore needs a grant that names the target's three existing save fields
(``plans/03-game-data.md`` section 44, ``plans/rounds/r11-keys.md``). For every dungeon here the DungeonParam row,
the census Banc folder and the ``DungeonInfo`` struct share one name, :attr:`KeyTarget.id`, and so does the label of
its English name in ``LocationMsg/Location.msbt`` (build e0f3ccfa; the name itself is read from the player's dump).

The Gerudo Fortress (row ``GerudoFortress_Adult``, logic item type ``HideoutSmallKey``) is not a target: its keys
have no logic dungeon and stay where the fill already keeps them. Keyless dungeons have no small key to send.
"""

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class KeyTarget:
    dungeon: str
    """The logic dungeon (``Item.dungeon`` and ``Region.dungeon``), e.g. ``Forest Temple``."""
    id: str
    """The native ``DungeonInfo.<id>`` struct, DungeonParam row and census Banc folder, e.g. ``ForestTemple``."""
    location_label: str
    """The label of the dungeon's name in ``LocationMsg/Location.msbt``; the name itself is read from the dump."""


_TARGETS = (
    KeyTarget("Forest Temple", "ForestTemple", "ForestTemple"),
    KeyTarget("Fire Temple", "FireTemple", "FireTemple"),
    KeyTarget("Water Temple", "WaterTemple", "WaterTemple"),
    KeyTarget("Shadow Temple", "ShadowTemple", "ShadowTemple"),
    KeyTarget("Spirit Temple", "SpiritTemple", "SpiritTemple"),
    KeyTarget("Bottom of the Well", "BottomOfTheWell", "BottomOfTheWell"),
    KeyTarget("Gerudo Training Ground", "GerudoTrainingGround", "GerudoTrainingGround"),
    KeyTarget("Ganons Castle", "InsideGanonCastle", "InsideGanonCastle"),
)

# The other dungeon-item families also exist in the three child dungeons and Ice Cavern.
DUNGEON_TARGETS = MappingProxyType(
    {
        target.dungeon: target
        for target in (
            *_TARGETS,
            KeyTarget("Deku Tree", "InsideTheDekuTree", "InsideTheDekuTree"),
            KeyTarget("Dodongos Cavern", "DodongoCavern", "DodongoCavern"),
            KeyTarget("Jabu Jabus Belly", "InsideJabuJabuBelly", "InsideJabuJabuBelly"),
            KeyTarget("Ice Cavern", "IceCavern", "IceCavern"),
        )
    }
)


@dataclass(frozen=True, order=True)
class DungeonGrant:
    """A source-bound reward. Only off-dungeon small keys need replacement pickup text."""

    target: str
    family: str
    named: bool = False

    @property
    def id(self) -> str:
        return self.target if self.named else f"{self.family}_{self.target}"

    @property
    def field(self) -> str:
        return f"DungeonInfo.{self.target}.IsGet{self.family}"


TARGETS: MappingProxyType[str, KeyTarget] = MappingProxyType({target.dungeon: target for target in _TARGETS})
"""Logic dungeon -> its target: every dungeon with logic small keys (``data/world/items.toml``)."""

BY_ID: MappingProxyType[str, KeyTarget] = MappingProxyType({target.id: target for target in TARGETS.values()})
"""Native ID -> target."""
