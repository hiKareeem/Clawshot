"""Named small-key get-window text: new labels appended, English names read from USen, nothing native touched."""

import pytest

from clawshot.formats import msbt, sarc, zsdic
from clawshot.formats.msbt import Msbt, Tag
from clawshot.patch import key_targets, key_text, text
from clawshot.patch.key_targets import KeyTarget
from clawshot.patch.plan import PatchError

GET = "EventFlowMsg/Get.msbt"
LOOKUP = b"\x02\x00XY"
NATIVE_GET = {
    "GetMessage": [Tag(2, 23, LOOKUP)],
    "SecondGetCaption": [Tag(2, 22, LOOKUP)],
    "GetCaption": [Tag(2, 19, LOOKUP)],
}
GROVE = [Tag(201, 0, b"\x01\x05\x00\x01"), "Grove ", Tag(0, 3, b"\x00\x00"), "Shrine", Tag(0, 3, b"\xff\xff")]
ENGLISH = {"GroveTemple": GROVE, "SandKeep": ["Sand  Keep\n"], "TrialGround": ["Proving Yard"]}
FOREIGN = {"GroveTemple": ["Hainschrein"], "SandKeep": ["Sandburg"], "TrialGround": ["Prüfhof"]}
POUCH = {key_text.KEY_NOUN: ["Tiny Key"], "Other_Name": ["Other"]}


def others(files, name):
    """The archive's members other than ``name``."""
    return {member: content for member, content in files.items() if member != name}


def message_label(message_id):
    return message_id.split(":")[1]


def _native():
    return {
        GET: msbt.write(Msbt({"B": [Tag(2, 23, b"\x01\x00")], "A": ["first"], "C": ["third"]}, buckets=2)),
        "EventFlowMsg/Other.msbt": msbt.write(Msbt({"X": ["x"]}, buckets=1)),
        "Other/Unrelated.bin": b"unrelated",
    }


def test_add_messages_appends_sorted_new_labels_and_keeps_everything_else():
    files = _native()
    additions = {GET: {"Zed": ["z"], "New": ["n", "", "ew", Tag(0, 4)]}}
    back = sarc.read(text.add_messages(additions)(sarc.write(files)))
    assert others(back, GET) == others(files, GET)
    original, document = msbt.read(files[GET]), msbt.read(back[GET])
    assert list(document.messages) == ["B", "A", "C", "New", "Zed"]
    assert document.messages["New"] == ["new", Tag(0, 4)]
    assert document.buckets == 2
    assert all(document.messages[label] == parts for label, parts in original.messages.items())
    kept = Msbt({label: document.messages[label] for label in original.messages}, document.buckets)
    assert msbt.write(kept) == files[GET]


@pytest.mark.parametrize(
    ("additions", "match"),
    [
        ({"EventFlowMsg/Nope.msbt": {"New": ["x"]}}, "no message file"),
        ({GET: {"New": ["x"], "A": ["overwrite"]}}, r"\['A'\] are already there"),
    ],
)
def test_add_messages_refuses_a_missing_file_or_a_label_already_there(additions, match):
    with pytest.raises(PatchError, match=match):
        text.add_messages(additions)(sarc.write(_native()))


def test_add_messages_will_not_add_a_label_twice():
    once = text.add_messages({GET: {"New": ["first"]}})(sarc.write(_native()))
    with pytest.raises(PatchError, match="already there"):
        text.add_messages({GET: {"New": ["second"]}})(once)
    assert msbt.read(sarc.read(once)[GET]).messages["New"] == ["first"]


@pytest.fixture
def targets(monkeypatch):
    synthetic = {
        "Grove Temple": KeyTarget(dungeon="Grove Temple", id="GroveTemple", location_label="GroveTemple"),
        "Sand Keep": KeyTarget(dungeon="Sand Keep", id="SandKeep_Adult", location_label="SandKeep"),
        "Trial Ground": KeyTarget(dungeon="Trial Ground", id="TrialGround", location_label="TrialGround"),
    }
    monkeypatch.setattr(key_text, "TARGETS", synthetic)
    return synthetic


def archive(locations, pouch=POUCH, get=NATIVE_GET):
    return sarc.write(
        {
            key_text.GET_TEXT: msbt.write(Msbt(dict(get), buckets=2)),
            key_text.LOCATION_TEXT: msbt.write(Msbt(dict(locations), buckets=3)),
            text.POUCH_TEXT: msbt.write(Msbt(dict(pouch), buckets=2)),
            "Other/Unrelated.bin": b"unrelated",
        }
    )


def write_romfs(root, zsdic_pack, archives):
    (root / "Pack").mkdir(parents=True)
    (root / "Mals").mkdir()
    (root / zsdic.PACK_PATH).write_bytes(zsdic_pack)
    dicts = zsdic.Dictionaries.from_pack(zsdic_pack)
    for language, data in archives.items():
        path = text.archive_path(language)
        (root / path).write_bytes(dicts.compress(path, data))
    return root


def apply(romfs, target_ids, language="USen"):
    """The language's archive before and after the change for ``target_ids``."""
    path = text.archive_path(language)
    data = zsdic.Dictionaries.from_romfs(romfs).decompress(path, (romfs / path).read_bytes())
    return data, key_text.changes(romfs, target_ids)[path](data)


def test_changes_add_the_same_english_pair_per_target_to_every_language(targets, tmp_path, zsdic_pack):
    pouch = {key_text.KEY_NOUN: [Tag(201, 0, b"\x02\x01"), "Winzling"]}
    romfs = write_romfs(tmp_path, zsdic_pack, {"USen": archive(ENGLISH), "EUde": archive(FOREIGN, pouch)})
    transforms = key_text.changes(romfs, ["SandKeep_Adult", "GroveTemple", "SandKeep_Adult"])
    assert set(transforms) == {text.archive_path("USen"), text.archive_path("EUde")}
    expected = {
        "Clawshot_SmallKey_GroveTemple_GetMessage": ["Tiny Key (Grove Shrine)"],
        "Clawshot_SmallKey_GroveTemple_GetCaption": ["Opens one locked door.\nDungeon: Grove Shrine"],
        "Clawshot_SmallKey_SandKeep_Adult_GetMessage": ["Tiny Key (Sand Keep)"],
        "Clawshot_SmallKey_SandKeep_Adult_GetCaption": ["Opens one locked door.\nDungeon: Sand Keep"],
    }
    named = {message_label(i) for target in ("GroveTemple", "SandKeep_Adult") for i in key_text.labels(target)}
    assert named == set(expected)
    for language in ("USen", "EUde"):
        before, after = (sarc.read(data) for data in apply(romfs, ["GroveTemple", "SandKeep_Adult"], language))
        assert others(after, key_text.GET_TEXT) == others(before, key_text.GET_TEXT)
        document = msbt.read(after[key_text.GET_TEXT])
        assert list(document.messages) == [*NATIVE_GET, *sorted(expected)]
        assert {label: document.messages[label] for label in NATIVE_GET} == NATIVE_GET
        assert {label: document.messages[label] for label in expected} == expected
        assert document.buckets == 2


def test_changes_read_the_location_label_and_ignore_target_order(targets, tmp_path, zsdic_pack):
    romfs = write_romfs(tmp_path, zsdic_pack, {"USen": archive(ENGLISH)})
    forward = apply(romfs, ["GroveTemple", "TrialGround"])[1]
    assert apply(romfs, ["TrialGround", "GroveTemple"])[1] == forward
    messages = msbt.read(sarc.read(forward)[key_text.GET_TEXT]).messages
    trial = [msbt.plain(messages[message_label(i)]) for i in key_text.labels("TrialGround")]
    grove = [msbt.plain(messages[message_label(i)]) for i in key_text.labels("GroveTemple")]
    assert trial == ["Tiny Key (Proving Yard)", "Opens one locked door.\nDungeon: Proving Yard"]
    assert trial[0] != grove[0] and trial[1] != grove[1]
    assert "Trial Ground" not in "".join(trial)


@pytest.mark.parametrize(
    ("target_ids", "locations", "pouch", "match"),
    [
        (["Nowhere"], ENGLISH, POUCH, "no small-key target"),
        (["GroveTemple"], {"SandKeep": ["Sand Keep"]}, POUCH, "no English message labelled GroveTemple"),
        (["GroveTemple"], {**ENGLISH, "GroveTemple": [Tag(201, 0, b"\x01"), " \n "]}, POUCH, "has no text"),
        (["GroveTemple"], ENGLISH, {"Other_Name": ["Other"]}, key_text.KEY_NOUN),
        (["GroveTemple"], ENGLISH, {key_text.KEY_NOUN: [Tag(201, 10, b"\x07\x00")]}, "has no text"),
    ],
)
def test_changes_refuse_unknown_targets_and_missing_or_blank_names(
    targets, tmp_path, zsdic_pack, target_ids, locations, pouch, match
):
    romfs = write_romfs(tmp_path, zsdic_pack, {"USen": archive(locations, pouch)})
    with pytest.raises(PatchError, match=match):
        key_text.changes(romfs, target_ids)


def test_changes_refuse_two_targets_with_one_english_name(targets, monkeypatch, tmp_path, zsdic_pack):
    monkeypatch.setitem(targets, "Copy Keep", KeyTarget(dungeon="Copy Keep", id="CopyKeep", location_label="CopyKeep"))
    romfs = write_romfs(tmp_path, zsdic_pack, {"USen": archive({**ENGLISH, "CopyKeep": ["Sand Keep"]})})
    with pytest.raises(PatchError, match="CopyKeep and SandKeep_Adult are both named 'Sand Keep'"):
        key_text.changes(romfs, ["SandKeep_Adult", "CopyKeep"])
    assert key_text.changes(romfs, ["CopyKeep"])


@pytest.mark.parametrize(
    ("extra", "match"),
    [
        (KeyTarget(dungeon="Other Grove", id="SandKeep_Adult", location_label="GroveTemple"), "claimed by"),
        (KeyTarget(dungeon="Bad", id="Bad:Id", location_label="SandKeep"), "cannot be part of a message label"),
    ],
)
def test_ambiguous_or_unusable_target_ids_are_refused(targets, monkeypatch, extra, match):
    monkeypatch.setitem(targets, extra.dungeon, extra)
    with pytest.raises(PatchError, match=match):
        key_text.labels("GroveTemple")


def test_changes_refuse_an_archive_without_the_get_file_or_with_a_label_taken(targets, tmp_path, zsdic_pack):
    romfs = write_romfs(tmp_path, zsdic_pack, {"USen": archive(ENGLISH)})
    transform = key_text.changes(romfs, ["GroveTemple"])[text.archive_path("USen")]
    files = sarc.read(archive(ENGLISH))
    del files[key_text.GET_TEXT]
    with pytest.raises(PatchError, match="no message file"):
        transform(sarc.write(files))
    taken = archive(ENGLISH, get={**NATIVE_GET, "Clawshot_SmallKey_GroveTemple_GetCaption": ["older"]})
    with pytest.raises(PatchError, match="already there"):
        transform(taken)


def test_no_targets_change_nothing(tmp_path):
    assert key_text.changes(tmp_path, []) == {}


@pytest.mark.dump
def test_dump_every_language_gains_only_the_same_english_pairs(romfs):
    ids = sorted({target.id for target in key_targets.TARGETS.values()})
    transforms = key_text.changes(romfs, ids)
    assert set(transforms) == {text.archive_path(language) for language in text.languages(romfs)}
    labels = sorted(message_label(i) for target in ids for i in key_text.labels(target))
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    english: dict[str, list] = {}
    for path, transform in sorted(transforms.items()):
        data = dicts.decompress(path, (romfs / path).read_bytes())
        before, after = sarc.read(data), sarc.read(transform(data))
        assert others(after, key_text.GET_TEXT) == others(before, key_text.GET_TEXT), path
        old, new = msbt.read(before[key_text.GET_TEXT]), msbt.read(after[key_text.GET_TEXT])
        assert list(new.messages) == [*old.messages, *labels], path
        assert {label: new.messages[label] for label in old.messages} == old.messages, path
        assert new.buckets == old.buckets, path
        added = {label: new.messages[label] for label in labels}
        english = english or added
        assert added == english, path
    mains = [msbt.plain(parts) for label, parts in english.items() if label.endswith("_GetMessage")]
    captions = [msbt.plain(parts) for label, parts in english.items() if label.endswith("_GetCaption")]
    assert len(set(mains)) == len(set(captions)) == len(ids)
    assert all(caption.startswith("Opens one locked door.\nDungeon: ") for caption in captions)
