"""Logic items and the remake actors that give them from a chest (``src/clawshot/data/item_actors.toml``).

    table = load()
    table.actor("Kokiri Sword")                                   # "Item_Sword_Kokiri"
    table.item("Item_Dungeon_Map", "Deku Tree", world.items)      # "Map (Deku Tree)"

Forwards, every logic item has one actor. Backwards, an actor names one item, except the actors shared by every
dungeon's own items (maps, compasses, keys), where the chest's dungeon picks it.
"""

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from clawshot.world.model import Item

ITEM_ACTORS_TOML = Path(__file__).resolve().parents[1] / "data" / "item_actors.toml"


class ItemActorError(ValueError):
    pass


@dataclass(frozen=True)
class ItemActors:
    actors: dict[str, str]
    """Logic item -> actor, in file order."""
    sources: dict[str, str]
    """Logic item -> where the pair comes from."""

    def actor(self, item: str) -> str:
        try:
            return self.actors[item]
        except KeyError:
            raise ItemActorError(f"no actor for the item {item!r} in item_actors.toml") from None

    def item(self, actor: str, dungeon: str | None, items: Mapping[str, Item]) -> str:
        """The logic item a chest holding ``actor`` gives, for a chest in ``dungeon`` (None outside dungeons)."""
        names = [name for name, a in self.actors.items() if a == actor]
        if len(names) > 1:
            names = [name for name in names if items[name].dungeon is not None and items[name].dungeon == dungeon]
        if len(names) != 1:
            where = f"in {dungeon}" if dungeon else "outside a dungeon"
            found = "no logic item" if not names else f"several logic items {names}"
            raise ItemActorError(f"item_actors.toml gives {found} for the actor {actor!r} {where}")
        return names[0]

    def check(self, items: Mapping[str, Item]) -> None:
        """Every item is one the logic knows, and an actor shared by several items only by one dungeon item each."""
        unknown = [name for name in self.actors if name not in items]
        if unknown:
            raise ItemActorError(f"item_actors.toml names items the world does not know: {unknown}")
        by_actor: dict[str, list[str]] = {}
        for name, actor in self.actors.items():
            by_actor.setdefault(actor, []).append(name)
        for actor, names in by_actor.items():
            if len(names) == 1:
                continue
            dungeons = [items[name].dungeon for name in names]
            if None in dungeons or len(set(dungeons)) != len(dungeons):
                raise ItemActorError(f"the actor {actor!r} gives {names}: only one item per dungeon may share it")


def loads(text: str) -> ItemActors:
    table = tomllib.loads(text).get("items", {})
    actors, sources = {}, {}
    for name, entry in table.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("actor"), str):
            raise ItemActorError(f"item_actors.toml: {name!r} needs an actor")
        actors[name] = entry["actor"]
        sources[name] = str(entry.get("source", ""))
    return ItemActors(actors, sources)


def load(path: str | Path = ITEM_ACTORS_TOML) -> ItemActors:
    return loads(Path(path).read_text(encoding="utf-8"))
