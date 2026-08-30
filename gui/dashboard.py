import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

from core.campaign import CampaignManager
from core.database import DatabaseManager
from anti_phishing import detector
from gui import report_generator

def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def format_table(rows, headers):
    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        # Fallback plaintext formatting
        print(" | ".join(headers))
        print("-" * 60)
        for row in rows:
            print(" | ".join(str(cell) for cell in row))


def view_campaigns():
    print_header("CAMPAIGN METRICS")
    mgr = CampaignManager()
    campaigns = mgr.get_all_campaigns()
    if not campaigns:
        print("No campaigns found.")
        return
    rows = []
    for camp in campaigns:
        rows.append([
            camp.get("id", "N/A"),
            camp.get("name", "Unnamed"),
            len(camp.get("targets", [])),
            camp.get("sent_count", 0),
            camp.get("opened_count", 0),
            camp.get("clicked_count", 0),
            camp.get("submitted_count", 0)
        ])
    format_table(rows, headers=["Campaign ID", "Name", "Targets", "Sent", "Opened", "Clicked", "Submitted"])


def view_sample_database():
    print_header("CAPTURED CREDENTIALS DATABASE")
    db = DatabaseManager()
    records = db.get_all()
    if not records:
        print("No credentials captured yet.")
        return
    rows = []
    for r in records:
        cid = r.get("id", "N/A")
        tmpl = r.get("template") or r.get("page", "N/A")
        user = r.get("username") or r.get("target", "N/A")
        pwd = r.get("password_hash") or r.get("hashed_value", "")
        pwd_trunc = pwd[:24] + "..." if pwd else "N/A"
        ts = r.get("timestamp", "N/A")
        rows.append([cid, tmpl, user, pwd_trunc, ts])

    format_table(rows, headers=["ID", "Template", "Username/Target", "Password Hash (truncated)", "Timestamp"])
    print("\nNote: Passwords are stored as Bcrypt hashes. No plaintext credentials are stored.")


def run_url_heuristics():
    print_header("ANTI-PHISHING URL HEURISTIC CHECK")
    sample_urls = [
        "https://mailsecure-accounts.example-training.local/signin/challenge",
        "http://192.168.1.55/login/verify",
        "https://accounts.google.com/signin",
        "https://socialconnect-secure-login.example-training.local/session/verify",
        "https://paypa1-security.com/account/confirm",
    ]
    rows = []
    for url in sample_urls:
        result = detector.analyze_url(url)
        rows.append([url, result.get("risk_level", "Unknown"), ", ".join(result.get("reasons", [])) or "-"])
    format_table(rows, headers=["URL", "Risk Level", "Reasons"])


def generate_report():
    print_header("GENERATING PDF REPORT")
    path = report_generator.generate_report()
    print(f"Report written to: {path}")


def main_menu():
    options = {
        "1": ("View campaign metrics", view_campaigns),
        "2": ("View captured credentials database", view_sample_database),
        "3": ("Run anti-phishing URL heuristics", run_url_heuristics),
        "4": ("Generate PDF report", generate_report),
        "5": ("Exit", None),
    }
    while True:
        print_header("SOCIAL ENGINEERING AWARENESS SIMULATOR - DASHBOARD")
        for key, (label, _) in options.items():
            print(f"  [{key}] {label}")
        choice = input("\nSelect an option: ").strip()
        if choice == "5":
            print("Goodbye.")
            break
        action = options.get(choice)
        if not action:
            print("Invalid choice.")
            continue
        action[1]()


if __name__ == "__main__":
    main_menu()
