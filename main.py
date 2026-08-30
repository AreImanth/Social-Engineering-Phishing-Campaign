"""
main.py

Unified entry point for the Social Engineering Awareness Simulator.

Launches the Flask demo server in a background thread, then drops the
instructor into the interactive CLI dashboard.

Run:
    python data/seed_data.py   # once, to populate synthetic sample data
    python main.py
"""

import os
import sys
import threading
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.app import app
from gui.dashboard import main_menu

HOST = "127.0.0.1"
PORT = 5000


def run_server():
    # use_reloader must be False since Flask's reloader doesn't play well
    # with running inside a background thread.
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    url = f"http://{HOST}:{PORT}/"
    print(f"\nDemo server running at {url}")
    print("(Training simulation only -- for local classroom use.)\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    main_menu()


if __name__ == "__main__":
    main()
