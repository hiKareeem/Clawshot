"""Get-window wordings (clawshot.patch.get_text) on synthetic names and lines, shaped as the game's are (grammar tags
included); no game text."""

import pytest

from clawshot.formats import msbt
from clawshot.formats.msbt import Tag
from clawshot.patch import get_text
from clawshot.patch.text import languages

MASC = Tag(201, 0, bytes([1, 0, 0, 1]))
FEM = Tag(201, 0, bytes([2, 1, 1, 1]))
FEM_PLURAL = Tag(201, 0, bytes([2, 3, 3, 2]))
NEUTER = Tag(201, 0, bytes([3, 2, 2, 1]))
DECLINED = Tag(201, 10, b"\x05\x00Kubek")  # a name told only by its declension table
PARTICLE = Tag(201, 7, b"\x03\x00\xec\x9d\x84\x03\x00\xeb\xa5\xbc")  # Korean object particle chosen at run time

ALL = [
    "CNzh", "EUde", "EUen", "EUes", "EUfr", "EUit", "EUnl", "EUpl", "EUru",
    "JPja", "KRko", "TWzh", "USen", "USes", "USfr", "USpt",
]  # fmt: skip


def own(language, name, line):
    out = get_text.possessive(language, name, line)
    return None if out is None else msbt.plain(out)


def test_every_message_language_has_a_wording():
    assert sorted(get_text.LANGUAGES) == ALL
    for language in ALL:
        nothing = get_text.nothing_texts(language)
        foreign = get_text.foreign_texts(language, "Kareem", "Morph Ball")
        assert set(nothing) == set(foreign) == {"_Name", "_Caption", "_GetMessage", "_GetCaption"}
        line = msbt.plain(foreign["_GetMessage"]).replace("\n", " ")  # rows break at spaces
        assert "Kareem" in line and "Morph Ball" in line, language
        assert "Kareem" in msbt.plain(foreign["_GetCaption"]), language
    with pytest.raises(ValueError, match="XXzz"):
        get_text.language("XXzz")


def test_foreign_lines_read_as_each_language_says_them():
    def line(language, player="Kareem", item="Morph Ball"):
        return msbt.plain(get_text.foreign_texts(language, player, item)["_GetMessage"]).replace("\n", " ")

    assert line("USen") == "You found Kareem's Morph Ball!"
    assert line("EUde") == "Du hast Morph Ball für Kareem gefunden!"
    assert line("EUfr") == "Vous avez trouvé Morph Ball pour Kareem !"
    assert line("USfr") == "Vous avez trouvé Morph Ball pour Kareem!"
    assert line("JPja") == "Kareemの" + "Morph Ballを見つけた！"
    assert line("KRko", item="모프 볼") == "Kareem의 모프 볼을 발견했다!"
    assert line("KRko", item="하트") == "Kareem의 하트를 발견했다!"
    assert line("KRko") == "Kareem의 Morph Ball을(를) 발견했다!"
    assert msbt.plain(get_text.nothing_texts("USen")["_GetMessage"]) == "You found Nothing."


def test_own_multiworld_items_say_your_where_no_gender_is_needed():
    def line(language, item="Progressive Wallet"):
        return msbt.plain(get_text.own_texts(language, item)["_GetMessage"]).replace("\n", " ")

    for language in ALL:
        texts = get_text.own_texts(language, "Progressive Wallet")
        assert set(texts) == {"_Name", "_Caption", "_GetMessage", "_GetCaption"}, language
        assert "Progressive Wallet" in line(language) and msbt.plain(texts["_GetCaption"]), language
    assert line("USen") == "You found your Progressive Wallet!"
    assert line("EUde") == "Du hast Progressive Wallet gefunden!"
    assert line("EUfr") == "Vous avez trouvé Progressive Wallet !"
    assert line("JPja") == "自分の" + "Progressive Walletを見つけた！"
    assert line("KRko") == "자신의 Progressive Wallet을(를) 발견했다!"


def test_names_from_other_games_are_made_safe_and_kept_to_two_rows():
    assert get_text.clean("  Morph\x00Ball 🎈 ", 32) == "Morph?Ball ?"
    long = get_text.clean("A" * 50, get_text.ITEM_MAX)
    assert long.endswith(get_text.ELLIPSIS) and get_text.cells(long) <= get_text.ITEM_MAX
    assert get_text.cells("ゼルダ") == 6
    for language in ALL:
        texts = get_text.foreign_texts(language, "P" * 30, "Ｉ" * 40)
        rows = msbt.plain(texts["_GetMessage"]).split("\n")
        assert len(rows) <= 3 and all(get_text.cells(row) <= get_text.ROW_WIDTH for row in rows), (language, rows)


def test_english_says_your_with_the_item_name():
    assert own("USen", ["Boomerang"], ["You found the Boomerang!"]) == "You found your Boomerang!"
    assert own("EUen", [Tag(201, 13, b""), "Gerudo Pass"], ["You got a gerudo pass!"]) == "You found your Gerudo Pass!"
    assert own("USen", ["Sword"], ["You got the sword!", Tag(0, 4, b""), "More."]) is None  # two pages stay


def test_european_articles_become_the_possessive():
    assert own("EUde", ["Bumerang"], ["Du hast den Bumerang gefunden!"]) == "Du hast deinen Bumerang gefunden!"
    assert (
        own("EUde", ["Große Tasche"], ["Du hast eine große Tasche erhalten!"]) == "Du hast deine große Tasche erhalten!"
    )
    assert own("EUde", ["Kleiner Schlüssel"], ["Du hast einen kleinen Schlüssel gefunden!"]) == (
        "Du hast deinen kleinen Schlüssel gefunden!"
    )
    # After "das" the adjective is weak, after "dein" mixed.
    assert own("EUde", ["Kleine Herz"], ["Du hast das kleine Herz erhalten!"]) == "Du hast dein kleines Herz erhalten!"
    assert own("EUde", ["5 Bomben"], ["Du hast 5 Bomben erhalten!"]) is None  # no article: the line stays
    assert own("EUfr", [MASC, "Arc"], ["Vous avez trouvé l'", MASC, "arc !"]) == "Vous avez trouvé votre arc !"
    assert own("EUfr", [FEM_PLURAL, "Bottes"], ["Vous avez les ", FEM_PLURAL, "bottes !"]) == "Vous avez vos bottes !"
    assert own("EUes", [FEM, "Llave"], ["¡Has encontrado una ", FEM, "llave!"]) == "¡Has encontrado tu llave!"
    assert own("USpt", [FEM, "Chave"], ["Você encontrou uma ", FEM, "chave!"]) == "Você encontrou a sua chave!"
    assert own("EUnl", ["Fles"], ["Je hebt een fles!"]) == "Je hebt je fles!"


def test_italian_elision_takes_the_gender_tag():
    assert own("EUit", [MASC, "Arco"], ["Hai trovato l'", MASC, "arco!"]) == "Hai trovato il tuo arco!"
    assert own("EUit", [FEM, "Ampolla"], ["Hai un'", FEM, "ampolla!"]) == "Hai la tua ampolla!"
    assert own("EUit", [MASC, "Arco"], ["Hai trovato gli ", MASC, "archi!"]) is None  # name not in the line


def test_tag_grammar_survives_the_edit():
    out = get_text.possessive("EUfr", [MASC, "Boomerang"], ["Vous avez trouvé le ", MASC, "boomerang !"])
    assert out == ["Vous avez trouvé votre ", MASC, "boomerang !"]


def test_asian_languages_put_your_before_the_name():
    assert own("JPja", ["ブーメラン"], ["ブーメランを見つけた！"]) == "自分のブーメランを見つけた！"
    assert get_text.possessive("KRko", ["부메랑"], ["부메랑", PARTICLE, " 발견했다!"]) == [
        "자신의 부메랑",
        PARTICLE,
        " 발견했다!",
    ]
    assert own("CNzh", ["回旋镖"], ["找到了回旋镖！"]) == "找到了你的回旋镖！"
    assert own("TWzh", ["回力鏢"], ["找到了回力鏢！"]) == "找到了你的回力鏢！"


def test_polish_and_russian_name_it_as_your_item():
    assert own("EUru", ["Бумеранг"], ["Вы нашли бумеранг!"]) == "Вы нашли свой предмет: Бумеранг!"
    assert get_text.possessive("EUpl", [DECLINED], ["Zdobyłeś kubek!"]) == [
        "Znalazłeś swój przedmiot: ",
        DECLINED,
        "!",
    ]


def test_languages_found_in_a_romfs_all_have_wordings(tmp_path):
    for language in ALL:
        (tmp_path / "Mals" / f"{language}.Product.110.sarc.zs").parent.mkdir(exist_ok=True)
        (tmp_path / "Mals" / f"{language}.Product.110.sarc.zs").write_bytes(b"")
    assert languages(tmp_path) == sorted(get_text.LANGUAGES)
