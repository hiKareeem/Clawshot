"""Click-only dialogs. Tk is imported/created on the main thread, never by headless/tests."""

import contextlib
import queue
import subprocess
import sys
import threading

from clawshot.app.paths import absolute_path, default_output_root

KINDS = {"dump-folder", "dump-file", "game", "output", "seeds", "emulator_mods", "tracker-seed", "tracker-save"}
CANCELLED = -128  # AppleScript's "User canceled." error number


def _title(kind):
    if kind == "dump-file":
        return "Choose your game .nup"
    if kind == "game":
        return "Choose Hookshot or Longshot game / launcher folder"
    return "Choose output parent folder" if kind == "output" else "Choose " + kind.replace("-", " ") + " folder"


def _applescript_text(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def macos_script(kind):
    """AppleScript for the standard macOS chooser, run by osascript in its own short-lived process.

    Tk inside the server process makes it a Cocoa app whose events nobody pumps between dialogs; it can stay
    frontmost and unresponsive after the dialog closes, and its hidden owner puts the panel in a screen corner.
    osascript activates itself, shows the panel centered and in front, and returns focus to the browser on exit.
    """
    prompt = "with prompt " + _applescript_text(_title(kind))
    if kind == "dump-file":
        choose = f'choose file {prompt} of type {{"nup"}}'
    else:
        choose = "choose folder " + prompt
        if kind == "output":
            choose += f" default location (POSIX file {_applescript_text(str(default_output_root().parent))})"
    return f"activate\nPOSIX path of ({choose})"


def choose_macos(kind):
    completed = subprocess.run(
        ["/usr/bin/osascript", "-e", macos_script(kind)], capture_output=True, text=True, encoding="utf-8"
    )
    if completed.returncode != 0:
        if f"({CANCELLED})" in completed.stderr:
            return None
        raise OSError(completed.stderr.strip() or f"osascript exited with {completed.returncode}")
    return completed.stdout.rstrip("\n") or None


def owner_geometry(window):
    """1x1 Tk owner at the browser window's center, so the dialog opens over the page, not in a screen corner."""
    if not window:
        return None
    return f"1x1+{window['x'] + window['width'] // 2}+{window['y'] + window['height'] // 2}"


def choose_tk(kind, window):
    import tkinter
    from tkinter import filedialog

    root = tkinter.Tk()
    try:
        geometry = owner_geometry(window)
        if geometry is None:
            root.withdraw()
        else:
            root.overrideredirect(True)
            root.geometry(geometry)
            with contextlib.suppress(tkinter.TclError):  # No compositor: a 1x1 borderless owner is still tiny.
                root.attributes("-alpha", 0.0)
            root.attributes("-topmost", True)
            root.update_idletasks()
            root.lift()
            root.focus_force()
        if kind == "dump-file":
            return filedialog.askopenfilename(parent=root, title=_title(kind), filetypes=[("NUP game dump", "*.nup")])
        return filedialog.askdirectory(
            parent=root,
            title=_title(kind),
            mustexist=True,
            initialdir=str(default_output_root().parent) if kind == "output" else None,
        )
    finally:
        root.destroy()


class BrowserDialogs:
    """HTTP thread submits; browser-mode main thread owns all Tcl/Tk calls. macOS uses osascript, never Tk."""

    def __init__(self, platform=sys.platform):
        self.requests = queue.Queue()
        self.lock = threading.Lock()
        self.platform = platform

    def choose(self, kind, window=None):
        if kind not in KINDS:
            raise ValueError("Unknown path chooser")
        if not self.lock.acquire(blocking=False):
            raise ValueError("A path chooser is already open")
        try:
            event, result = threading.Event(), {}
            self.requests.put((kind, window, event, result))
            event.wait()
            if "error" in result:
                raise ValueError(result["error"])
            return result.get("path")
        finally:
            self.lock.release()

    def run(self):
        while True:
            try:
                kind, window, event, result = self.requests.get(timeout=0.25)
            except queue.Empty:
                continue
            try:
                value = choose_macos(kind) if self.platform == "darwin" else choose_tk(kind, window)
                result["path"] = (
                    str(absolute_path(value, "Selected path", allow_links=kind not in ("output", "emulator_mods")))
                    if value
                    else None
                )
            except Exception as error:
                result["error"] = f"Path chooser unavailable: {error}. Paste a path instead."
            finally:
                event.set()


def webview_chooser(window, webview):
    lock = threading.Lock()
    dialog_types = getattr(webview, "FileDialog", None)
    open_dialog = dialog_types.OPEN if dialog_types is not None else webview.OPEN_DIALOG
    folder_dialog = dialog_types.FOLDER if dialog_types is not None else webview.FOLDER_DIALOG

    def choose(kind, _browser_window=None):  # pywebview already parents its dialog to the app window
        if kind not in KINDS:
            raise ValueError("Unknown path chooser")
        if not lock.acquire(blocking=False):
            raise ValueError("A path chooser is already open")
        try:
            if kind == "dump-file":
                selected = window.create_file_dialog(
                    open_dialog, allow_multiple=False, file_types=("NUP game dump (*.nup)",)
                )
            else:
                selected = window.create_file_dialog(folder_dialog, allow_multiple=False)
            if not selected:
                return None
            return str(absolute_path(selected[0], "Selected path", allow_links=kind not in ("output", "emulator_mods")))
        finally:
            lock.release()

    return choose
