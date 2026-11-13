"""Fresh seed users inherit options/account only; fixtures are synthetic, no game starts."""

import os

import pytest

from clawshot.pack.runtime import prepare_user


def snapshot(root):
    return {
        path.relative_to(root): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in root.rglob("*")
        if path.is_file()
    }


def account(game, name, *, option=True, profile=True, modified=100):
    root = game / "user/save" / name
    root.mkdir(parents=True)
    for filename, present in [("option.sav", option), ("account.sav", profile)]:
        if present:
            (root / filename).write_bytes(("synthetic " + name + filename).encode())
    (root / "slot_01").mkdir()
    (root / "slot_01/progress.sav").write_bytes(b"NEVER import this playthrough")
    os.utime(root, (modified, modified))
    return root


@pytest.mark.parametrize("program", ["hookshot", "longshot"])
def test_fresh_user_inherits_only_newest_accounts_options_once(tmp_path, program):
    game = tmp_path / program
    account(game, "old-id", modified=100)
    newest = account(game, "new-id", modified=200)
    user = tmp_path / "seed-user"
    plan = {"cwd": str(game), "user": str(user)}
    before = snapshot(game)
    result = prepare_user(plan)
    assert result["copied"] == ["option.sav", "account.sav"] and result["missing"] == []
    assert {path.as_posix(): path.read_bytes() for path in user.rglob("*") if path.is_file()} == {
        (user / "save/new-id/option.sav").as_posix(): (newest / "option.sav").read_bytes(),
        (user / "save/new-id/account.sav").as_posix(): (newest / "account.sav").read_bytes(),
    }
    assert snapshot(game) == before
    seeded = snapshot(user)
    (newest / "option.sav").write_bytes(b"normal options changed after first Play")
    assert prepare_user(plan)["copied"] == []
    assert snapshot(user) == seeded
    assert not list(user.rglob("slot_*"))


@pytest.mark.parametrize("option,profile", [(True, False), (False, True), (False, False)])
def test_missing_newest_files_are_reported_without_older_fallback(tmp_path, option, profile):
    game = tmp_path / "game"
    account(game, "older-complete", modified=100)
    newest = account(game, "newest", option=option, profile=profile, modified=200)
    user = tmp_path / "user"
    result = prepare_user({"cwd": str(game), "user": str(user)})
    present = [name for name in ("option.sav", "account.sav") if (newest / name).is_file()]
    missing = [name for name in ("option.sav", "account.sav") if name not in present]
    assert result["copied"] == present and result["missing"] == missing
    assert all(name in result["message"] for name in missing)
    assert {path.relative_to(user).as_posix() for path in user.rglob("*") if path.is_file()} == {
        "save/newest/" + name for name in present
    }


def test_no_normal_user_creates_empty_user_and_reports_skipped_options(tmp_path):
    user = tmp_path / "new-user"
    result = prepare_user({"cwd": str(tmp_path / "game"), "user": str(user)})
    assert result["missing"] == ["option.sav", "account.sav"] and result["copied"] == []
    assert user.is_dir() and list(user.iterdir()) == []


def test_existing_seed_files_and_progress_are_never_changed(tmp_path):
    game = tmp_path / "game"
    account(game, "source")
    user = tmp_path / "seed/user"
    account(user.parent, "seed-id")
    before = snapshot(user)
    result = prepare_user({"cwd": str(game), "user": str(user)})
    assert result["copied"] == [] and result["missing"] == []
    assert snapshot(user) == before
