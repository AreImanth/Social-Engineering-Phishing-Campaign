"""
core/tracker.py

Emulates phishing-email dispatch and open/click tracking using a 1x1
tracking pixel, for teaching purposes. No actual email is ever sent by
this project -- "sending" just marks a campaign target's 'sent' flag so
the dashboard has something to show. The tracking pixel route in
server/app.py calls into this module to flip 'opened' / 'clicked' flags
only -- it never receives form content.
"""

from core import campaign

# A minimal valid 1x1 transparent PNG, served by the tracking pixel route.
TRACKING_PIXEL_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000155ee5c150000000049454e44ae426082"
)


def simulate_send(campaign_id: str, target: str) -> bool:
    """Mark a target as 'sent' (emulated -- no real email is dispatched)."""
    return campaign.record_event(campaign_id, target, "sent")


def register_open(campaign_id: str, target: str) -> bool:
    """Called when the tracking pixel is loaded (email 'opened')."""
    return campaign.record_event(campaign_id, target, "opened")


def register_click(campaign_id: str, target: str) -> bool:
    """Called when the target clicks through to the mock login page."""
    return campaign.record_event(campaign_id, target, "clicked")


def register_awareness_redirect(campaign_id: str, target: str) -> bool:
    """
    Called when the target is redirected to the awareness page after
    'submitting' the demo login form. Records only that a submission
    happened -- never what was typed.
    """
    return campaign.record_event(campaign_id, target, "submitted")
