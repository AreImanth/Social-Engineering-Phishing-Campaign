"""
data/seed_data.py

Populates the demo with fully SYNTHETIC sample data using CampaignManager
and DatabaseManager so the operator dashboard and PDF report have
data to display in the exact expected schema.
"""

import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.campaign import CampaignManager
from core.database import DatabaseManager
from core.hashing import SecurityHasher

FICTIONAL_TARGETS = [
    "student01@classroom-demo.local",
    "student02@classroom-demo.local",
    "student03@classroom-demo.local",
    "student04@classroom-demo.local",
    "student05@classroom-demo.local",
    "student06@classroom-demo.local",
]

SAMPLE_VALUES = [
    "SamplePass!001", "SamplePass!002", "SamplePass!003",
    "SamplePass!004", "SamplePass!005", "SamplePass!006",
]

DEMO_TEMPLATES = ["facebook", "google", "netflix"]


def seed_campaign():
    camp_mgr = CampaignManager()
    campaign = camp_mgr.create_campaign(
        campaign_id="demo-campaign",
        name="Q3 Classroom Awareness Exercise",
        template="facebook",
        targets=FICTIONAL_TARGETS,
    )
    for i, target in enumerate(FICTIONAL_TARGETS):
        camp_mgr.record_event("demo-campaign", target, "sent")
        if i % 5 != 4:
            camp_mgr.record_event("demo-campaign", target, "opened")
        if i % 3 != 2:
            camp_mgr.record_event("demo-campaign", target, "clicked")
        if i % 2 == 0:
            camp_mgr.record_event("demo-campaign", target, "submitted")


def seed_sample_database():
    db = DatabaseManager()
    for i, target in enumerate(FICTIONAL_TARGETS):
        if i % 2 != 0:
            continue  # only "submitted" targets have a sample record
        sample_value = SAMPLE_VALUES[i % len(SAMPLE_VALUES)]
        hashed_val = SecurityHasher.hash_bcrypt(sample_value)
        template_name = DEMO_TEMPLATES[i % len(DEMO_TEMPLATES)]
        db.save_credential(template_name, target, hashed_val, "127.0.0.1", "Mozilla/5.0 (Demo)")


if __name__ == "__main__":
    seed_campaign()
    seed_sample_database()
    print("Synthetic sample data seeded successfully:")
    print(f"  - {len(FICTIONAL_TARGETS)} fictional campaign targets")
    print(f"  - Sample 'captured' records written to data/captured_credentials.json")
    print("  - No real credentials were ever involved in generating this data.")
