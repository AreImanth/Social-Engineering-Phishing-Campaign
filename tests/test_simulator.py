"""
tests/test_simulator.py

Automated unit tests for the awareness demo's functional modules.
Run with:  python -m pytest tests/
"""

import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHashing(unittest.TestCase):
    def test_bcrypt_round_trip(self):
        from core import hashing
        plaintext = "example-value-123"
        hashed = hashing.hash_with_bcrypt(plaintext)
        self.assertNotEqual(plaintext, hashed)
        self.assertTrue(hashing.verify_bcrypt(plaintext, hashed))
        self.assertFalse(hashing.verify_bcrypt("wrong-value", hashed))

    def test_sha256_deterministic(self):
        from core import hashing
        h1 = hashing.hash_with_sha256("abc", salt="salt-")
        h2 = hashing.hash_with_sha256("abc", salt="salt-")
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)


class TestCampaignAndDatabase(unittest.TestCase):
    def setUp(self):
        # Redirect data dir to a temp directory for isolated testing
        self.tmp_dir = tempfile.mkdtemp()
        import core.campaign as campaign_mod
        import core.database as database_mod
        self._orig_campaign_file = campaign_mod.CAMPAIGN_FILE
        self._orig_db_file = database_mod.CREDENTIALS_FILE
        campaign_mod.CAMPAIGN_FILE = os.path.join(self.tmp_dir, "campaign_state.json")
        database_mod.CREDENTIALS_FILE = os.path.join(self.tmp_dir, "captured_credentials.json")
        self.campaign_mod = campaign_mod
        self.database_mod = database_mod

    def tearDown(self):
        import core.campaign as campaign_mod
        import core.database as database_mod
        campaign_mod.CAMPAIGN_FILE = self._orig_campaign_file
        database_mod.CREDENTIALS_FILE = self._orig_db_file
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_campaign_lifecycle(self):
        self.campaign_mod.create_campaign("c1", "Test Campaign", ["a@x.local", "b@x.local"])
        self.campaign_mod.record_event("c1", "a@x.local", "sent")
        self.campaign_mod.record_event("c1", "a@x.local", "clicked")
        summary = self.campaign_mod.campaign_summary("c1")
        self.assertEqual(summary["total_targets"], 2)
        self.assertEqual(summary["sent"], 1)
        self.assertEqual(summary["clicked"], 1)
        self.assertEqual(summary["submitted"], 0)

    def test_campaign_invalid_event_raises(self):
        self.campaign_mod.create_campaign("c2", "Test", ["a@x.local"])
        with self.assertRaises(AssertionError):
            self.campaign_mod.record_event("c2", "a@x.local", "not_a_real_event")

    def test_database_write_and_read(self):
        self.database_mod.write_record({"target": "a@x.local", "hashed_value": "abc123"})
        records = self.database_mod.read_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["target"], "a@x.local")

    def test_database_clear(self):
        self.database_mod.write_record({"target": "a@x.local"})
        self.database_mod.clear_all()
        self.assertEqual(self.database_mod.read_all(), [])


class TestAntiPhishingDetector(unittest.TestCase):
    def test_flags_raw_ip(self):
        from anti_phishing import detector
        result = detector.analyze_url("http://192.168.1.10/login")
        self.assertEqual(result["risk_level"], "high")
        self.assertTrue(any("IP address" in r for r in result["reasons"]))

    def test_flags_typosquat(self):
        from anti_phishing import detector
        result = detector.analyze_url("https://paypa1-security.com/confirm")
        self.assertEqual(result["risk_level"], "high")
        self.assertTrue(any("typosquat" in r.lower() for r in result["reasons"]))

    def test_clean_url_low_risk(self):
        from anti_phishing import detector
        result = detector.analyze_url("https://accounts.google.com/signin")
        self.assertEqual(result["risk_level"], "low")

    def test_batch_analysis(self):
        from anti_phishing import detector
        urls = ["https://accounts.google.com/signin", "http://10.0.0.1/verify"]
        results = detector.analyze_batch(urls)
        self.assertEqual(len(results), 2)


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        from server.app import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_index_lists_pages(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"socialconnect", resp.data)

    def test_phish_page_serves_and_records_click(self):
        resp = self.client.get("/phish/socialconnect/test-campaign/test-target")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"SocialConnect", resp.data)

    def test_unknown_page_404(self):
        resp = self.client.get("/phish/not-a-real-page/c1/t1")
        self.assertEqual(resp.status_code, 404)

    def test_tracking_pixel_returns_png(self):
        resp = self.client.get("/phish/track/test-campaign/test-target.png")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "image/png")

    def test_event_endpoint_rejects_invalid_event(self):
        resp = self.client.post("/phish/event", json={
            "campaign_id": "c1", "target": "t1", "event": "not_allowed"
        })
        self.assertEqual(resp.status_code, 400)

    def test_event_endpoint_ignores_extra_fields(self):
        # Even if extra fields (e.g. fake "username"/"password") are sent,
        # the endpoint must not echo, store, or otherwise expose them.
        resp = self.client.post("/phish/event", json={
            "campaign_id": "c1", "target": "t1", "event": "submitted",
            "username": "should-be-ignored", "password": "should-be-ignored",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(b"should-be-ignored", resp.data)

    def test_awareness_page_renders(self):
        resp = self.client.get("/phish/awareness")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"simulated phishing attempt", resp.data)


if __name__ == "__main__":
    unittest.main()
