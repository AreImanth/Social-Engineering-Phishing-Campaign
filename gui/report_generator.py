"""
gui/report_generator.py

Compiles a clean, tabular PDF security-awareness report using ReportLab.
"""

import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)

from core.campaign import CampaignManager
from core.database import DatabaseManager

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
REPORT_PATH = os.path.join(DATA_DIR, "campaign_report.pdf")


def generate_report(output_path: str = REPORT_PATH) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#b00020"))
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                             topMargin=0.7 * inch, bottomMargin=0.7 * inch)
    story = []

    story.append(Paragraph("Security Awareness Simulation — Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        "This report summarizes a classroom phishing-awareness exercise. "
        "All captured credentials are from simulated training runs — passwords are stored as Bcrypt hashes.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 0.3 * inch))

    # --- Campaign metrics table ---
    story.append(Paragraph("Campaign Metrics", styles["Heading2"]))
    mgr = CampaignManager()
    campaigns = mgr.get_all_campaigns()
    table_data = [["Campaign ID", "Name", "Targets", "Sent", "Opened", "Clicked", "Submitted", "Click Rate"]]
    for camp in campaigns:
        targets_list = camp.get("targets", [])
        num_targets = len(targets_list) if isinstance(targets_list, list) else 0
        clicked_count = camp.get("clicked_count", 0)
        click_rate = f"{(clicked_count / num_targets * 100):.0f}%" if num_targets > 0 else "0%"
        
        table_data.append([
            camp.get("id", "N/A"),
            camp.get("name", "Unnamed"),
            num_targets,
            camp.get("sent_count", 0),
            camp.get("opened_count", 0),
            clicked_count,
            camp.get("submitted_count", 0),
            click_rate
        ])

    if len(table_data) == 1:
        story.append(Paragraph("No campaign data available.", styles["Normal"]))
    else:
        t = Table(table_data, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#b00020")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)

    story.append(Spacer(1, 0.35 * inch))

    # --- Captured credentials table ---
    story.append(Paragraph("Captured Credentials (Hashed)", styles["Heading2"]))
    story.append(Paragraph(
        "Entries below show simulated captured credentials. Passwords are Bcrypt-hashed.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 0.1 * inch))
    db = DatabaseManager()
    records = db.get_all()
    sample_table = [["ID", "Template/Page", "Username/Target", "Password Hash (truncated)", "Timestamp"]]
    for r in records[:20]:
        pwd = r.get("password_hash") or r.get("hashed_value", "")
        pwd_trunc = (pwd[:28] + "...") if pwd else "N/A"
        sample_table.append([
            str(r.get("id", "N/A")),
            r.get("template") or r.get("page", "N/A"),
            r.get("username") or r.get("target", "N/A"),
            pwd_trunc,
            r.get("timestamp", "N/A"),
        ])
    if len(sample_table) == 1:
        story.append(Paragraph("No credentials captured yet.", styles["Normal"]))
    else:
        t2 = Table(sample_table, hAlign="LEFT")
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t2)

    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph("Key Takeaways for Students", styles["Heading2"]))
    for bullet in [
        "Look closely at the URL bar before entering credentials anywhere.",
        "Urgency and fear-based language is a classic social-engineering trigger.",
        "Legitimate services rarely ask you to 're-verify' your account via an emailed link.",
        "Report suspicious messages to IT/security instead of clicking through.",
    ]:
        story.append(Paragraph(f"• {bullet}", styles["Normal"]))

    doc.build(story)
    return output_path


if __name__ == "__main__":
    path = generate_report()
    print(f"Report generated at: {path}")
