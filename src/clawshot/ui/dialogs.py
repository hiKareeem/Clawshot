"""Click-only dialogs. Tk is imported/created on the main thread, never by headless/tests."""

import queue
import threading

from clawshot.app.paths import absolute_path, default_output_root

KINDS = {"dump-folder", "dump-file", "hookshot", "output"}


class BrowserDialogs:
    """HTTP thread submits; browser-mode main thread owns all Tcl/Tk calls (including macOS)."""

    def __init__(self):
        self.requests = queue.Queue()
        self.lock = threading.Lock()

    def choose(self, kind):
        if kind not in KINDS:
            raise ValueError("Unknown path chooser")
        if not self.lock.acquire(blocking=False):
            raise ValueError("A path chooser is already open")
        try:
            event, result = threading.Event(), {}
            self.requests.put((kind, event, result))
            event.wait()
            if "error" in result:
                raise ValueError(result["error"])
            return result.get("path")
        finally:
            self.lock.release()

    def run(self):
        while True:
            try:
                kind, event, result = self.requests.get(timeout=0.25)
            except queue.Empty:
                continue
            root = None
            try:
                import tkinter
                from tkinter import filedialog

                root = tkinter.Tk()
                root.withdraw()
                if kind == "dump-file":
                    value = filedialog.askopenfilename(
                        parent=root, title="Choose your game .nup", filetypes=[("NUP game dump", "*.nup")]
                    )
                else:
                    title = (
                        "Choose output parent folder"
                        if kind == "output"
                        else "Choose " + kind.replace("-", " ") + " folder"
                    )
                    value = filedialog.askdirectory(
                        parent=root,
                        title=title,
                        mustexist=True,
                        initialdir=str(default_output_root().parent) if kind == "output" else None,
                    )
                result["path"] = str(absolute_path(value, "Selected path")) if value else None
            except Exception as error:
                result["error"] = f"Path chooser unavailable: {error}. Paste a path instead."
            finally:
                if root is not None:
                    root.destroy()
                event.set()


def webview_chooser(window, webview):
    lock = threading.Lock()

    def choose(kind):
        if kind not in KINDS:
            raise ValueError("Unknown path chooser")
        if not lock.acquire(blocking=False):
            raise ValueError("A path chooser is already open")
        try:
            if kind == "dump-file":
                selected = window.create_file_dialog(
                    webview.OPEN_DIALOG, allow_multiple=False, file_types=("NUP game dump (*.nup)",)
                )
            else:
                selected = window.create_file_dialog(webview.FOLDER_DIALOG, allow_multiple=False)
            if not selected:
                return None
            return str(absolute_path(selected[0], "Selected path"))
        finally:
            lock.release()

    return choose
