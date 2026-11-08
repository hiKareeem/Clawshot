"""Shop identities and sale parameters; game resources are read only from the player's dump.

A shelf actor is not the sale definition. The linked NPC's ShopRef component owns
GoodsList[ShopItemIndex]; its Actor selects the price, pouch item and UI text.
"""

import copy
import tomllib
from dataclasses import dataclass
from pathlib import Path

from clawshot.formats import byml, sarc, zsdic
from clawshot.patch.plan import PatchError

SHOPS_TOML = Path(__file__).resolve().parents[1] / "data" / "shops.toml"
POUCH_TABLE = "RSDB/PouchActorInfo.Product.111.rstbl.byml.zs"


@dataclass(frozen=True)
class Slot:
    id: int
    shop: str
    location: str
    file: str
    owner: str
    owner_id: int
    member: str
    index: int
    vanilla_item: str
    price: int

    @property
    def pack(self) -> str:
        return f"Pack/Actor/{self.owner}.pack.zs"


def load(path: str | Path = SHOPS_TOML) -> tuple[Slot, ...]:
    with Path(path).open("rb") as stream:
        data = tomllib.load(stream)
    slots = tuple(Slot(**{**row, "id": int(row["id"]), "owner_id": int(row["owner_id"])}) for row in data["slot"])
    if len({slot.id for slot in slots}) != len(slots):
        raise PatchError("shops.toml: repeated actor Hash")
    return slots


def actor_name(path: str) -> str:
    return path.rsplit("/", 1)[-1].split(".", 1)[0]


def actor_path(actor: str) -> str:
    return f"Work/Actor/{actor}.engine__actor__ActorParam.gyml"


def member_path(path: str) -> str:
    return path.removeprefix("?").removeprefix("Work/").replace(".gyml", ".bgyml")


def resolve_member(pack: dict[str, bytes], path: str) -> dict:
    """Resolve BYML parent inheritance within one actor pack, including component maps."""
    node = byml.read(pack[member_path(path)])
    result = resolve_member(pack, node["$parent"]) if "$parent" in node else {}
    for key, value in node.items():
        if key == "Components":
            result[key] = result.get(key, {}) | value
        elif key != "$parent":
            result[key] = copy.deepcopy(value)
    return result


def validate(romfs: str | Path, slots: tuple[Slot, ...] | None = None) -> None:
    """Check every committed shelf Hash against Banc, its linked seller and its sale/price rows."""
    romfs = Path(romfs)
    slots = load() if slots is None else slots
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def resource(path: str) -> bytes:
        return dictionaries.decompress(path, (romfs / path).read_bytes())

    pouch = {row["__RowId"]: row for row in byml.read(resource(POUCH_TABLE))}
    trees = {}
    packs = {}
    for slot in slots:
        if slot.file not in trees:
            trees[slot.file] = {int(actor["Hash"]): actor for actor in byml.read(resource(slot.file))["Actors"]}
        if slot.pack not in packs:
            packs[slot.pack] = sarc.read(resource(slot.pack))
        actors, pack = trees[slot.file], packs[slot.pack]
        actor, owner = actors[slot.id], actors[slot.owner_id]
        if actor["Gyaml"] != slot.vanilla_item or int(actor.get("Dynamic", {}).get("ShopItemIndex", 0)) != slot.index:
            raise PatchError(f"{slot.file}: stale shelf definition for {slot.id}: {actor}")
        links = {int(link["Dst"]) for link in owner.get("Links", []) if link["Gyaml"] in ("ForSale", "Reference")}
        if owner["Gyaml"] != slot.owner or slot.id not in links:
            raise PatchError(f"{slot.file}: {slot.id} is not linked to seller {slot.owner_id}")
        component = resolve_member(pack, actor_path(slot.owner))["Components"]["ShopRef"]
        if member_path(component) != slot.member:
            raise PatchError(f"{slot.owner}: ShopRef changed to {component}")
        goods = resolve_member(pack, component)["GoodsList"][slot.index]
        price = int(pouch[slot.vanilla_item].get("BuyingPrice", 0)) + int(goods.get("PriceOffset", 0))
        if actor_name(goods["Actor"]) != slot.vanilla_item or price != slot.price:
            raise PatchError(f"{slot.owner}[{slot.index}]: stale sale definition: {goods}, price {price}")
