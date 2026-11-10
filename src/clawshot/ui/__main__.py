"""Local Clawshot UI, optionally embedded in pywebview; --no-open never creates a window."""

import argparse
import multiprocessing
import webbrowser

from clawshot.app.preferences import Preferences, user_preferences_path
from clawshot.ui.dialogs import BrowserDialogs, webview_chooser
from clawshot.ui.server import Application, LocalServer, serve_in_thread


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-open", action="store_true", help="print a local URL; never open a window/browser")
    args = parser.parse_args(argv)
    server = LocalServer(Application(preferences=Preferences(user_preferences_path())))
    print(f"Clawshot UI: {server.url}", flush=True)
    print("Local only. Keep this terminal running; Ctrl+C stops it and cancels its worker.", flush=True)
    try:
        if args.no_open:
            server.serve_forever()
        else:
            try:
                import webview
            except ImportError:
                dialogs = BrowserDialogs()
                server.app.chooser = dialogs.choose
                server.app.allow_open = True
                server.app.allow_play = True
                thread = serve_in_thread(server)
                try:
                    webbrowser.open(server.url)
                    dialogs.run()
                finally:
                    server.shutdown()
                    thread.join()
            else:
                thread = serve_in_thread(server)
                try:
                    window = webview.create_window("Clawshot", server.url, width=1120, height=860, min_size=(620, 600))
                    server.app.chooser = webview_chooser(window, webview)
                    server.app.allow_open = True
                    server.app.allow_play = True
                    webview.start()
                finally:
                    server.shutdown()
                    thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
