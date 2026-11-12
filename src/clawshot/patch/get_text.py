"""Get-window text in every message language: "You found Nothing.", "You found <Player>'s <Item>!", "You found your
<Item>!".

The get window shows two lines of the item's own (``ActorMsg/PouchContent.msbt``: ``<key>_GetMessage`` then
``<key>_GetCaption``; ``plans/03-game-data.md`` section 22), so these are written per item key and per language:

- **Nothing** and **another player's item** are new keys (``clawshot.patch.custom_items``). Their lines are built
  here from :data:`LANGUAGES`: one fixed wording per language. A player's and an item's name come from another game,
  so they have no grammatical gender or case here; every wording keeps them out of agreement (German "Du hast <Item>
  für <Player> gefunden!", Russian "Вы нашли предмет игрока <Player>: <Item>!", Japanese
  "<Player>の<Item>を見つけた！"). Korean's object particle follows the item name's last syllable
  (:func:`korean_object`).
- **The player's own item** keeps the game's own line, with "your" put in the way each language says it
  (:func:`possessive`): English "You found your <Name>!"; the article before the name swapped for the possessive in
  the European languages (``den`` -> ``deinen``, ``la`` -> ``votre``, ``l'`` -> ``il tuo``/``la tua`` from the
  name's gender tag, ``de``/``het``/``een`` -> ``je``), "自分の" / "자신의" / "你的" before the name in Japanese,
  Korean and Chinese; Polish and Russian, whose possessive would agree with a gender the text does not record, name
  it as "your item: <Name>". Where the line does not have the expected shape (no article, a name told by a
  declension tag) the game's line stays as it is: correct, only without "your".

The item's gender comes from the name's grammar tag (group 201 type 0: byte 0 the gender, 1 masculine, 2 feminine,
3 neuter; byte 3 the number, 2 plural), read from the dump, never stored here. Wordings are Clawshot's own text.
"""

import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from clawshot.formats import msbt
from clawshot.formats.msbt import Part, Tag

GRAMMAR = 201
GENDER_TAG = 0  # group 201 type 0: gender, article forms, number
ROW_WIDTH = 40  # display cells a row of the get window; the game's own get lines break at 39-40 Latin characters
PLAYER_MAX = 16  # Archipelago's longest player name
ITEM_MAX = 32  # display cells of an item name, so a line keeps to two rows
ELLIPSIS = "…"


@dataclass(frozen=True)
class Language:
    nothing_name: str
    nothing_get: str
    nothing_caption: str
    foreign_get: str  # {player}, {item}; Korean also {object} (the particle)
    foreign_caption: str  # {player}
    foreign_name: str  # {player}, {item}
    possessive: str  # the rule :func:`possessive` applies to the player's own items
    own_get: str = ""  # {item}; Korean also {object}: a multiworld item of the player's own (OWN)
    own_caption: str = ""


# The 16 message archives of the dump. EU and US variants of a language share a wording unless the game's own lines
# address the player differently (EUes "Has encontrado" against USes "Encontraste").
LANGUAGES: Mapping[str, Language] = {
    "USen": Language(
        "Nothing",
        "You found Nothing.",
        "Better luck next time!",
        "You found {player}'s {item}!",
        "It's on its way to {player}.",
        "{player}'s {item}",
        "en",
    ),
    "EUde": Language(
        "Nichts",
        "Du hast nichts gefunden.",
        "Vielleicht hast du nächstes Mal mehr Glück!",
        "Du hast {item} für {player} gefunden!",
        "Der Fund wird an {player} geschickt.",
        "{item} ({player})",
        "de",
    ),
    "EUfr": Language(
        "Rien",
        "Vous n'avez rien trouvé.",
        "Vous aurez plus de chance la prochaine fois !",
        "Vous avez trouvé {item} pour {player} !",
        "Cet objet va être envoyé à {player}.",
        "{item} ({player})",
        "fr",
    ),
    "EUes": Language(
        "Nada",
        "No has encontrado nada.",
        "¡Más suerte la próxima vez!",
        "¡Has encontrado {item} para {player}!",
        "Este objeto se enviará a {player}.",
        "{item} ({player})",
        "es",
    ),
    "USes": Language(
        "Nada",
        "No encontraste nada.",
        "¡Más suerte la próxima vez!",
        "¡Encontraste {item} para {player}!",
        "Este objeto se enviará a {player}.",
        "{item} ({player})",
        "es",
    ),
    "EUit": Language(
        "Niente",
        "Non hai trovato niente.",
        "Andrà meglio la prossima volta!",
        "Hai trovato {item} per {player}!",
        "Questo oggetto verrà inviato a {player}.",
        "{item} ({player})",
        "it",
    ),
    "USpt": Language(
        "Nada",
        "Você não encontrou nada.",
        "Mais sorte na próxima vez!",
        "Você encontrou {item} para {player}!",
        "Este item será enviado para {player}.",
        "{item} ({player})",
        "pt",
    ),
    "EUnl": Language(
        "Niets",
        "Je hebt niets gevonden.",
        "Volgende keer beter!",
        "Je hebt {item} voor {player} gevonden!",
        "Dit voorwerp wordt naar {player} gestuurd.",
        "{item} ({player})",
        "nl",
    ),
    "EUpl": Language(
        "Nic",
        "Nic nie znalazłeś.",
        "Więcej szczęścia następnym razem!",
        "Znalazłeś przedmiot gracza {player}: {item}!",
        "Ten przedmiot zostanie wysłany do gracza {player}.",
        "{item} ({player})",
        "pl",
    ),
    "EUru": Language(
        "Ничего",
        "Вы ничего не нашли.",
        "Повезёт в следующий раз!",
        "Вы нашли предмет игрока {player}: {item}!",
        "Он будет отправлен игроку {player}.",
        "{item} ({player})",
        "ru",
    ),
    "JPja": Language(
        "なにもなし",
        "なにも見つからなかった…",
        "次はきっと いいことがあるよ！",
        "{player}の{item}を見つけた！",
        "{player}のもとへ送られる！",
        "{player}の{item}",
        "ja",
    ),
    "KRko": Language(
        "꽝",
        "아무것도 찾지 못했다…",
        "다음에는 운이 좋을 거야!",
        "{player}의 {item}{object} 발견했다!",
        "{player}에게 보내진다!",
        "{player}의 {item}",
        "ko",
    ),
    "CNzh": Language(
        "什么都没有",
        "什么都没有找到……",
        "下次运气会更好！",
        "找到了{player}的{item}！",
        "这件物品将送给{player}。",
        "{player}的{item}",
        "zh",
    ),
    "TWzh": Language(
        "什麼都沒有",
        "什麼都沒有找到……",
        "下次運氣會更好！",
        "找到了{player}的{item}！",
        "這件物品將送給{player}。",
        "{player}的{item}",
        "zh",
    ),
}
# EUen is worded as USen (the game's lines are the same). Canadian French (USfr) sets no space before "!".
LANGUAGES = {
    **LANGUAGES,
    "EUen": LANGUAGES["USen"],
    "USfr": Language(
        "Rien",
        "Vous n'avez rien trouvé.",
        "Vous aurez plus de chance la prochaine fois!",
        "Vous avez trouvé {item} pour {player}!",
        "Cet objet va être envoyé à {player}.",
        "{item} ({player})",
        "fr",
    ),
}


# The player's own item when the multiworld gives it (a progressive one): its name is the multiworld's, with no
# grammatical gender, so the wordings keep it out of agreement; "your" is said where that needs no gender (English,
# Polish and Russian "your item: <Item>", Japanese, Korean, Chinese) and the caption says "for you" elsewhere.
OWN: Mapping[str, tuple[str, str]] = {
    "USen": ("You found your {item}!", "It's yours now."),
    "EUen": ("You found your {item}!", "It's yours now."),
    "EUde": ("Du hast {item} gefunden!", "Der Fund gehört dir."),
    "EUfr": ("Vous avez trouvé {item} !", "Cet objet est pour vous."),
    "USfr": ("Vous avez trouvé {item}!", "Cet objet est pour vous."),
    "EUes": ("¡Has encontrado {item}!", "Este objeto es para ti."),
    "USes": ("¡Encontraste {item}!", "Este objeto es para ti."),
    "EUit": ("Hai trovato {item}!", "Questo oggetto è per te."),
    "USpt": ("Você encontrou {item}!", "Este item é seu."),
    "EUnl": ("Je hebt {item} gevonden!", "Dit voorwerp is voor jou."),
    "EUpl": ("Znalazłeś swój przedmiot: {item}!", "Ten przedmiot należy do ciebie."),
    "EUru": ("Вы нашли свой предмет: {item}!", "Этот предмет ваш."),
    "JPja": ("自分の{item}を見つけた！", "これは自分のものだ！"),
    "KRko": ("자신의 {item}{object} 발견했다!", "이것은 자신의 것이다!"),
    "CNzh": ("找到了你的{item}！", "这件物品是你的。"),
    "TWzh": ("找到了你的{item}！", "這件物品是你的。"),
}
LANGUAGES = {code: Language(*[getattr(lang, f) for f in ("nothing_name", "nothing_get", "nothing_caption",
                                                          "foreign_get", "foreign_caption", "foreign_name",
                                                          "possessive")], *OWN[code])
             for code, lang in LANGUAGES.items()}  # fmt: skip


def language(name: str) -> Language:
    if name not in LANGUAGES:
        raise ValueError(f"no get-window wording for the message language {name!r}")
    return LANGUAGES[name]


# --- names from another game ------------------------------------------------------------------------------------


def cells(text: str) -> int:
    """Display width: wide and full-width characters take two cells."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def clean(text: str, limit: int) -> str:
    """A name from another game made safe for a message: control and private-use characters and characters outside
    the Basic Multilingual Plane (which the game's fonts lack) become ``?``, runs of space become one, and a name
    wider than ``limit`` cells is cut with an ellipsis."""
    out = []
    for c in " ".join(text.split()):
        category = unicodedata.category(c)
        out.append("?" if ord(c) > 0xFFFF or category in ("Cc", "Cf", "Co", "Cs", "Cn") else c)
    text = "".join(out).strip() or "?"
    if cells(text) <= limit:
        return text
    while text and cells(text) + 1 > limit:
        text = text[:-1]
    return text.rstrip() + ELLIPSIS


def korean_object(word: str) -> str:
    """The object particle after ``word``: 을 after a final consonant, 를 after a vowel, 을(를) after anything that
    is not a Hangul syllable (a Latin name's reading is not known)."""
    last = word.rstrip()[-1:] or " "
    if "가" <= last <= "힣":
        return "을" if (ord(last) - 0xAC00) % 28 else "를"
    return "을(를)"


def wrap(text: str, width: int = ROW_WIDTH) -> str:
    """``text`` broken into rows of at most ``width`` cells, at spaces; a word wider than a row (Chinese or Japanese
    text has no spaces) is broken where it reaches the edge. Punctuation set off by a space (French "Kareem !")
    stays with the word before it."""
    words: list[str] = []
    for word in text.split(" "):
        if words and word and all(unicodedata.category(c).startswith("P") for c in word):
            words[-1] += " " + word
        else:
            words.append(word)
    rows: list[str] = []
    row = ""
    for word in words:
        candidate = f"{row} {word}" if row else word
        if cells(candidate) <= width:
            row = candidate
            continue
        if row:
            rows.append(row)
        row = ""
        for c in word:
            if cells(row + c) > width:
                rows.append(row)
                row = ""
            row += c
    rows.append(row)
    return "\n".join(rows)


def nothing_texts(name: str) -> dict[str, list[Part]]:
    """The Nothing item's ``_Name``, ``_Caption``, ``_GetMessage`` and ``_GetCaption`` in language ``name``."""
    lang = language(name)
    return {
        "_Name": [lang.nothing_name],
        "_Caption": [wrap(lang.nothing_caption)],
        "_GetMessage": [wrap(lang.nothing_get)],
        "_GetCaption": [wrap(lang.nothing_caption)],
    }


def foreign_texts(name: str, player: str, item: str) -> dict[str, list[Part]]:
    """Another player's item's texts in language ``name``."""
    lang = language(name)
    player, item = clean(player, PLAYER_MAX), clean(item, ITEM_MAX)
    values = {"player": player, "item": item, "object": korean_object(item)}
    caption = wrap(lang.foreign_caption.format(**values))
    return {
        "_Name": [lang.foreign_name.format(**values)],
        "_Caption": [caption],
        "_GetMessage": [wrap(lang.foreign_get.format(**values))],
        "_GetCaption": [caption],
    }


def own_texts(name: str, item: str) -> dict[str, list[Part]]:
    """The player's own multiworld item's texts (a progressive item the multiworld gives) in language ``name``."""
    lang = language(name)
    item = clean(item, ITEM_MAX)
    caption = wrap(lang.own_caption)
    return {
        "_Name": [item],
        "_Caption": [caption],
        "_GetMessage": [wrap(lang.own_get.format(item=item, object=korean_object(item)))],
        "_GetCaption": [caption],
    }


# --- the player's own items -------------------------------------------------------------------------------------


def gender(name_parts: Sequence[Part]) -> tuple[int, bool] | None:
    """(gender, plural) from the name's grammar tag: gender 1 masculine, 2 feminine, 3 neuter; None without one."""
    for part in name_parts:
        if isinstance(part, Tag) and (part.group, part.type) == (GRAMMAR, GENDER_TAG) and len(part.params) >= 4:
            return part.params[0], part.params[3] == 2
    return None


def _replace(parts: Sequence[Part], start: int, end: int, new: str) -> list[Part]:
    """``parts`` with the visible text ``[start, end)`` (offsets in :func:`msbt.plain`) replaced by ``new``; the span
    lies in text parts, tags around it stay."""
    out: list[Part] = []
    offset = 0
    placed = False
    for part in parts:
        if not isinstance(part, str):
            out.append(part)
            continue
        lo, hi = offset, offset + len(part)
        offset = hi
        if hi <= start or lo >= end and placed:
            out.append(part)
            continue
        keep_before = part[: max(0, start - lo)]
        keep_after = part[max(0, end - lo) :] if end <= hi else ""
        out.append(keep_before + ("" if placed else new) + keep_after)
        placed = True
    if not placed:
        out.append(new)
    return msbt.normalized(out)


def _name_start(message: str, name: str, stem: bool = False) -> int | None:
    """Where the name's first word starts in the message (case aside), after a space or an elided article. With
    ``stem`` a first word of several (an adjective) may end differently in the line (German "Kleiner Schlüssel",
    "einen kleinen Schlüssel")."""
    words = name.split()
    if not words:
        return None
    lower = message.lower()
    candidates = [words[0].lower()]
    if stem and len(words) > 1 and len(words[0]) > 3:
        candidates.append(words[0].lower()[:-1])
    for first in candidates:
        at = lower.find(first)
        while at > 0:
            if message[at - 1] in " '’":
                return at
            at = lower.find(first, at + 1)
    return None


def _article(message: str, at: int) -> tuple[int, str]:
    """The word before position ``at`` (with its trailing space or apostrophe): (start, word as written)."""
    before = message[:at]
    if before.endswith(("'", "’")):
        stem = before[:-1]
        start = max(stem.rfind(" "), -1) + 1
        return start, before[start:]
    stripped = before.rstrip(" ")
    start = stripped.rfind(" ") + 1
    return start, before[start:]


# Article (lower case, as it stands before the name) -> possessive, per language; a callable decides by gender.
def _italian(word: str, grammar: tuple[int, bool] | None) -> str | None:
    fixed = {"il": "il tuo", "lo": "il tuo", "un": "il tuo", "uno": "il tuo", "la": "la tua", "una": "la tua",
             "i": "i tuoi", "gli": "i tuoi", "le": "le tue"}  # fmt: skip
    if word in fixed:
        return fixed[word]
    if word in ("l'", "l’", "un'", "un’") and grammar is not None:
        masculine, plural = grammar[0] != 2, grammar[1]
        return {(True, False): "il tuo", (False, False): "la tua", (True, True): "i tuoi", (False, True): "le tue"}[
            (masculine, plural)
        ]
    return None


ARTICLES: Mapping[str, Mapping[str, str] | Callable[[str, tuple[int, bool] | None], str | None]] = {
    "de": {"den": "deinen", "einen": "deinen", "die": "deine", "eine": "deine", "das": "dein", "ein": "dein"},
    "fr": {
        "le": "votre",
        "la": "votre",
        "l'": "votre",
        "l’": "votre",
        "un": "votre",
        "une": "votre",
        "les": "vos",
        "des": "vos",
    },  # fmt: skip
    "es": {
        "el": "tu",
        "la": "tu",
        "un": "tu",
        "una": "tu",
        "los": "tus",
        "las": "tus",
        "unos": "tus",
        "unas": "tus",
    },  # fmt: skip
    "pt": {"o": "o seu", "a": "a sua", "um": "o seu", "uma": "a sua", "os": "os seus", "as": "as suas"},
    "nl": {"de": "je", "het": "je", "een": "je"},
    "it": _italian,
}
GENERIC = {"pl": "Znalazłeś swój przedmiot: ", "ru": "Вы нашли свой предмет: "}
PREFIX = {"ja": "自分の", "ko": "자신의 "}
INSERT = {"zh": "你的"}


def _has_break(parts: Sequence[Part]) -> bool:
    return any(isinstance(p, str) and "\n" in p or isinstance(p, Tag) and (p.group, p.type) == (0, 4) for p in parts)


def possessive(name: str, name_parts: Sequence[Part], message: Sequence[Part]) -> list[Part] | None:
    """The player's own item's get line saying "your", in language ``name``, from the item's ``_Name`` and the game's
    ``_GetMessage``; None where the game's line should stay (the module docstring)."""
    rule = language(name).possessive
    name_parts, message = list(name_parts), list(message)
    visible_name = msbt.plain(name_parts).strip()
    if rule == "en":
        if _has_break(message) or not visible_name:
            return None
        return msbt.normalized(["You found your ", *name_parts, "!"])
    plain = msbt.plain(message)
    if rule in GENERIC:
        # A name told only by a declension tag (Polish) shows its nominative, which the colon calls for.
        if not visible_name and not any(isinstance(p, Tag) and p.group == GRAMMAR for p in name_parts):
            return None
        return msbt.normalized([GENERIC[rule], *name_parts, "!"])
    if rule in PREFIX:
        if not visible_name or not plain.startswith(visible_name):
            return None
        return msbt.normalized([PREFIX[rule], *message])
    if rule in INSERT:
        at = plain.find(visible_name)
        return None if at < 0 or not visible_name else _replace(message, at, at, INSERT[rule])
    at = _name_start(plain, visible_name, stem=rule == "de")
    if at is None:
        return None
    start, word = _article(plain, at)
    table = ARTICLES[rule]
    key = word.strip().lower()
    new = table(key, gender(name_parts)) if callable(table) else table.get(key)
    if new is None:
        return None
    capital = word[:1].isupper()
    new = (new[:1].upper() + new[1:] if capital else new) + " "
    out = _replace(message, start, at, new)
    if rule == "de" and key == "das" and len(visible_name.split()) > 1:
        # After "das" the adjective is weak (das kleine), after "dein" mixed (dein kleines).
        shift = len(new) - (at - start)
        adjective_end = at + shift + len(visible_name.split()[0])
        if msbt.plain(out)[adjective_end - 1 : adjective_end] == "e":
            out = _replace(out, adjective_end, adjective_end, "s")
    return out
