import json
import os
import threading
from datetime import datetime, timezone

class CampaignManager:
    def __init__(self, state_path=None):
        if state_path is None:
            DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
            state_path = os.path.join(DATA_DIR, "campaign_state.json")
        self.state_path = state_path
        self._lock = threading.Lock()
        self._ensure_storage()

    def _ensure_storage(self):
        dir_name = os.path.dirname(self.state_path)
        os.makedirs(dir_name, exist_ok=True)
        if not os.path.exists(self.state_path):
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump({"campaigns": {}}, f)

    def _read_raw_state(self):
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"campaigns": {}}

    def _write_raw_state(self, state):
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
        except IOError as e:
            print(f"Error saving campaign state: {e}")

    def _normalize_campaign(self, campaign_id, raw_camp):
        """Normalizes campaign data whether created via simple GUI or seed_data dict structure."""
        name = raw_camp.get("name", "Unnamed Campaign")
        template = raw_camp.get("template", "facebook")
        status = raw_camp.get("status", "Active")
        created_at = raw_camp.get("created_at", "")

        targets_raw = raw_camp.get("targets", {})
        if isinstance(targets_raw, dict):
            # Format from seed_data: { "email1": {"sent": True, ...}, "email2": ... }
            targets_list = list(targets_raw.keys())
            sent_count = sum(1 for t in targets_raw.values() if t.get("sent"))
            opened_count = sum(1 for t in targets_raw.values() if t.get("opened"))
            clicked_count = sum(1 for t in targets_raw.values() if t.get("clicked"))
            submitted_count = sum(1 for t in targets_raw.values() if t.get("submitted"))
        elif isinstance(targets_raw, list):
            # Format from GUI creator
            targets_list = targets_raw
            sent_count = raw_camp.get("sent_count", len(targets_list))
            opened_count = raw_camp.get("opened_count", 0)
            clicked_count = raw_camp.get("clicked_count", 0)
            submitted_count = raw_camp.get("submitted_count", 0)
        else:
            targets_list = []
            sent_count = opened_count = clicked_count = submitted_count = 0

        return {
            "id": str(campaign_id),
            "name": name,
            "template": template,
            "targets": targets_list,
            "sent_count": sent_count,
            "opened_count": opened_count,
            "clicked_count": clicked_count,
            "submitted_count": submitted_count,
            "status": status,
            "created_at": created_at,
            "raw_targets": targets_raw
        }

    def create_campaign(self, campaign_id=None, name="New Campaign", template="facebook", targets=None):
        if targets is None:
            targets = []

        with self._lock:
            state = self._read_raw_state()
            campaigns = state.get("campaigns", {})
            
            if campaign_id is None:
                campaign_id = str(len(campaigns) + 1)
            else:
                campaign_id = str(campaign_id)

            target_dict = {
                t: {"sent": True, "opened": False, "clicked": False, "submitted": False}
                for t in targets
            }

            campaign_data = {
                "name": name,
                "template": template,
                "status": "Active",
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "targets": target_dict
            }

            campaigns[campaign_id] = campaign_data
            state["campaigns"] = campaigns
            self._write_raw_state(state)
            
            return self._normalize_campaign(campaign_id, campaign_data)

    def get_campaign(self, campaign_id):
        with self._lock:
            state = self._read_raw_state()
            campaigns = state.get("campaigns", {})
            cid_str = str(campaign_id)
            if cid_str in campaigns:
                return self._normalize_campaign(cid_str, campaigns[cid_str])
            return None

    def get_all_campaigns(self):
        with self._lock:
            state = self._read_raw_state()
            campaigns = state.get("campaigns", {})
            res = []
            for cid, raw in campaigns.items():
                res.append(self._normalize_campaign(cid, raw))
            return res

    def record_event(self, campaign_id, target_or_event, event_type=None):
        """
        Supports two signatures:
          record_event(campaign_id, "click")
          record_event(campaign_id, target_email, "clicked")
        """
        with self._lock:
            state = self._read_raw_state()
            campaigns = state.get("campaigns", {})
            cid_str = str(campaign_id)

            if cid_str not in campaigns:
                return False

            camp = campaigns[cid_str]
            targets_raw = camp.get("targets", {})

            if event_type is None:
                # Signature: record_event(campaign_id, "click")
                evt = target_or_event
                target = None
            else:
                # Signature: record_event(campaign_id, target_email, "clicked")
                target = target_or_event
                evt = event_type

            # Normalize event name
            if evt in ["click", "clicked"]:
                evt_key = "clicked"
            elif evt in ["open", "opened"]:
                evt_key = "opened"
            elif evt in ["submit", "submitted"]:
                evt_key = "submitted"
            elif evt in ["sent"]:
                evt_key = "sent"
            else:
                return False

            if isinstance(targets_raw, dict):
                if target and target in targets_raw:
                    targets_raw[target][evt_key] = True
                else:
                    # If target not specified or unknown, mark for first target or overall
                    for t_data in targets_raw.values():
                        if not t_data.get(evt_key):
                            t_data[evt_key] = True
                            break
            elif isinstance(targets_raw, list):
                count_key = f"{evt_key}_count"
                camp[count_key] = camp.get(count_key, 0) + 1

            self._write_raw_state(state)
            return True
