"""Shop identities and sale parameters; game resources are read only from the player's dump.

A shelf actor is not the sale definition. The linked NPC's ShopRef component owns
GoodsList[ShopItemIndex]; its Actor selects the price, pouch item and UI text.
"""

import copy
import tomllib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from clawshot.formats import byml, sarc, zsdic
from clawshot.patch.plan import PatchError
from clawshot.settings import DEFAULTS, shop_price

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


@dataclass(frozen=True)
class Sale:
    actor: str
    display: str
    base_price: int
    bundle: int = 1
    price: int | None = None


def patch_shelves(data: bytes, changes: tuple[tuple[Slot, Sale], ...]) -> bytes:
    """Replace shelf models, retaining Hash, index, position and seller links.

    Quantity boards belong to the old bundle. Replace their count or remove them
    for a single item; sold-out boards are controlled by the seller and stay.
    """
    document = byml.load(data)
    actors = {int(actor["Hash"]): actor for actor in document.root["Actors"]}
    removed = set()
    for slot, sale in changes:
        actor = actors.get(slot.id)
        if actor is None or actor["Gyaml"] != slot.vanilla_item:
            raise PatchError(f"{slot.file}: shelf {slot.id} no longer holds {slot.vanilla_item}")
        actor["Gyaml"] = sale.display
        links = []
        for link in actor.get("Links", []):
            board = actors.get(int(link["Dst"]))
            if board is not None and board["Gyaml"].startswith("Shop_Board_Bundle_"):
                if sale.bundle == 1:
                    removed.add(int(board["Hash"]))
                    continue
                board["Gyaml"] = f"Shop_Board_Bundle_{sale.bundle:02d}"
            links.append(link)
        if "Links" in actor:
            actor["Links"] = links
    if removed:
        document.root["Actors"] = [actor for actor in document.root["Actors"] if int(actor["Hash"]) not in removed]
        for actor in document.root["Actors"]:
            if "Links" in actor:
                actor["Links"] = [link for link in actor["Links"] if int(link["Dst"]) not in removed]
        for key in ("FarDeleteGroups", "SimultaneousGroups"):
            if key in document.root:
                document.root[key] = [
                    [actor_hash for actor_hash in group if int(actor_hash) not in removed]
                    for group in document.root[key]
                ]
    result = byml.dump(document)
    if difference := byml.difference(document.root, byml.read(result)):
        raise PatchError(f"shop shelves failed read-back: {difference}")
    return result


def patch_goods(data: bytes, changes: tuple[tuple[Slot, Sale], ...]) -> bytes:
    """Change sale/display together. Preserve destination price/discounts unless an exact price is requested."""
    pack = sarc.read(data)
    members = {}
    seen = {}
    for slot, sale in changes:
        key = (slot.member, slot.index)
        if key in seen:
            if seen[key] != sale:
                raise PatchError(f"{slot.pack}: conflicting sales for {key}")
            continue
        seen[key] = sale
        if slot.member not in members:
            members[slot.member] = byml.load(pack[slot.member])
        document = members[slot.member]
        # Resolve inheritance only to find the existing list; retain all unrelated fields.
        if "GoodsList" not in document.root:
            document.root["GoodsList"] = resolve_member(pack, slot.member)["GoodsList"]
        goods = document.root["GoodsList"][slot.index]
        if actor_name(goods["Actor"]) != slot.vanilla_item:
            raise PatchError(f"{slot.pack}: sale {slot.index} no longer holds {slot.vanilla_item}: {goods}")
        goods["Actor"] = actor_path(sale.actor)
        price = slot.price if sale.price is None else sale.price
        goods["PriceOffset"] = byml.I32(price - sale.base_price)
        if sale.price is not None and "ConditionalPriceOffsetList" in goods:
            # Exact-price settings must not become negative after the vanilla soldier discount.
            goods["ConditionalPriceOffsetList"] = []
    for name, document in members.items():
        pack[name] = byml.dump(document)
        if difference := byml.difference(document.root, byml.read(pack[name])):
            raise PatchError(f"{name}: shop goods failed read-back: {difference}")
    result = sarc.write(pack)
    if sarc.read(result) != pack:
        raise PatchError("shop seller pack failed read-back")
    return result


def member_growth(before: bytes, after: bytes) -> dict[str, int]:
    """Rounded raw growth of changed ShopParams whose parsed allocation cannot grow.

    Seller edits only replace actors/prices or remove conditional discounts. Keep
    the original per-member parsed overhead; this is not a generic bgyml formula.
    """
    original, changed = sarc.read(before), sarc.read(after)
    growth = {}
    editable = {"Actor", "PriceOffset", "ConditionalPriceOffsetList"}
    for name, data in changed.items():
        if not name.startswith("Component/ShopParam/") or original.get(name) == data:
            continue
        if name not in original:
            raise PatchError(f"{name}: a new ShopParam has no original allocation")
        old, new = byml.read(original[name]), byml.read(data)
        old_goods, new_goods = old.get("GoodsList", []), new.get("GoodsList", [])
        if len(old_goods) != len(new_goods) or not byml.same(
            {k: v for k, v in old.items() if k != "GoodsList"},
            {k: v for k, v in new.items() if k != "GoodsList"},
        ):
            raise PatchError(f"{name}: ShopParam structure needs a new allocation formula")
        for left, right in zip(old_goods, new_goods, strict=True):
            if not byml.same(
                {k: v for k, v in left.items() if k not in editable},
                {k: v for k, v in right.items() if k not in editable},
            ) or len(right.get("ConditionalPriceOffsetList", [])) > len(left.get("ConditionalPriceOffsetList", [])):
                raise PatchError(f"{name}: ShopParam structure needs a new allocation formula")
        delta = ((len(data) + 31) // 32 - (len(original[name]) + 31) // 32) * 32
        if delta > 0:
            growth[name] = delta
    return growth


def changes(
    romfs: str | Path,
    sales: Mapping[str, str],
    *,
    displays: Mapping[str, str] | None = None,
    slots: tuple[Slot, ...] | None = None,
    prices: Mapping[str, int] | None = None,
) -> dict[str, Callable[[bytes], bytes]]:
    """Decompressed resource transforms for logical slot -> sale actor.

    By default display and sale agree and must be native Shop actors. ``displays``
    explicitly requests a stand-in experiment, never used by normal seed output.
    Compression, size-table changes and output validation belong to the writer.
    """
    romfs = Path(romfs)
    slots = load() if slots is None else slots
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    pouch = {
        row["__RowId"]: row
        for row in byml.read(dictionaries.decompress(POUCH_TABLE, (romfs / POUCH_TABLE).read_bytes()))
    }
    known = {slot.location for slot in slots}
    if unknown := sales.keys() - known:
        raise PatchError(f"unknown shop locations: {sorted(unknown)}")
    if unknown := (prices or {}).keys() - sales.keys():
        raise PatchError(f"prices need a sale actor for locations: {sorted(unknown)}")
    shelves, owners = {}, {}
    for slot in slots:
        if slot.location not in sales:
            continue
        actor = sales[slot.location]
        display = (displays or {}).get(slot.location, actor)
        if not display.startswith("Shop_") or display.startswith("Shop_Board_"):
            raise PatchError(f"{slot.location}: no native shop display for {display}")
        if actor not in pouch or not (romfs / f"Pack/Actor/{display}.pack.zs").is_file():
            raise PatchError(f"{slot.location}: unknown sale actor or display: {actor}, {display}")
        price = (prices or {}).get(slot.location)
        if actor == slot.vanilla_item and display == slot.vanilla_item and price is None:
            continue
        row = pouch[actor]
        sale = Sale(actor, display, int(row.get("BuyingPrice", 0)), int(row.get("BundleActorNum", 1)), price)
        if sale.bundle > 1 and not (romfs / f"Pack/Actor/Shop_Board_Bundle_{sale.bundle:02d}.pack.zs").is_file():
            raise PatchError(f"{slot.location}: no quantity board for bundle {sale.bundle}")
        if display != slot.vanilla_item:
            shelves.setdefault(slot.file, []).append((slot, sale))
        owners.setdefault(slot.pack, []).append((slot, sale))
    return {
        **{path: partial(patch_shelves, changes=tuple(rows)) for path, rows in shelves.items()},
        **{path: partial(patch_goods, changes=tuple(rows)) for path, rows in owners.items()},
    }


def native_items(path: str | Path = SHOPS_TOML) -> dict[str, dict]:
    with Path(path).open("rb") as stream:
        data = tomllib.load(stream)
    items = dict(data["items"])
    for alias, target in data.get("display_aliases", {}).items():
        items[alias] = items[target]
    return items


def patch_step(
    romfs: str | Path,
    locations: tuple[str, ...],
    *,
    shop_prices: str = DEFAULTS["shop_prices"],
    cheap_deku_shield: bool = DEFAULTS["cheap_deku_shield"],
) -> Callable[[Mapping[str, str]], dict]:
    """Shuffle selected shelves; price settings also cover an unshuffled Kokiri Deku Shield."""
    palette = native_items()
    slots = load()

    def step(placements: Mapping[str, str]) -> dict[str, Callable[[bytes], bytes]]:
        sales = {}
        for name in locations:
            item = placements[name]
            if item not in palette:
                raise PatchError(f"{name}: {item!r} has no native shop display")
            sales[name] = palette[item]["display"]
        prices = {}
        for slot in slots:
            actor = sales.get(slot.location, slot.vanilla_item)
            price = shop_price(
                slot.shop,
                actor,
                slot.price,
                shuffled=slot.location in locations,
                policy=shop_prices,
                cheap_shield=cheap_deku_shield,
            )
            if price != slot.price or (slot.location in locations and shop_prices == "affordable"):
                sales.setdefault(slot.location, actor)
                prices[slot.location] = price
        return changes(romfs, sales, slots=slots, prices=prices) if sales else {}

    return step
