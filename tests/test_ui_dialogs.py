"""Dialog adapters without opening any OS dialog: the macOS script text and Tk owner placement are pure."""

import subprocess

from clawshot.ui import dialogs


def test_macos_uses_osascript_not_tk_and_quotes_its_text(monkeypatch, tmp_path):
    calls = []

    def run(argv, **_):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout=str(tmp_path) + "\n", stderr="")

    monkeypatch.setattr(dialogs.subprocess, "run", run)
    monkeypatch.setattr(dialogs, "choose_tk", lambda *_: (_ for _ in ()).throw(AssertionError("Tk on macOS")))
    assert dialogs.choose_macos("dump-folder") == str(tmp_path)
    assert calls[0][:2] == ["/usr/bin/osascript", "-e"]
    script = calls[0][2]
    assert script.startswith("activate\n") and "choose folder" in script
    assert 'choose file with prompt "Choose your game .nup" of type {"nup"}' in dialogs.macos_script("dump-file")
    monkeypatch.setattr(dialogs, "default_output_root", lambda: tmp_path / 'odd "name\\' / "Clawshot")
    assert 'odd \\"name\\\\' in dialogs.macos_script("output")


def test_macos_cancel_is_none_and_failure_is_an_error(monkeypatch):
    results = iter(
        [
            subprocess.CompletedProcess([], 1, stdout="", stderr="execution error: User canceled. (-128)"),
            subprocess.CompletedProcess([], 1, stdout="", stderr="execution error: boom (-1)"),
        ]
    )
    monkeypatch.setattr(dialogs.subprocess, "run", lambda *_, **__: next(results))
    assert dialogs.choose_macos("seeds") is None
    try:
        dialogs.choose_macos("seeds")
    except OSError as error:
        assert "boom" in str(error)
    else:
        raise AssertionError("expected an error")


def test_tk_owner_sits_at_the_browser_window_center():
    assert dialogs.owner_geometry(None) is None
    assert dialogs.owner_geometry({"x": -1440, "y": 25, "width": 1200, "height": 801}) == "1x1+-840+425"
