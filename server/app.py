import os
import sys

# Ensure server/ is on path so email_sender can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, Response

from email_sender import send_campaign_emails
from core.hashing import SecurityHasher
from core.campaign import CampaignManager
from core.database import DatabaseManager
from anti_phishing import detector
from gui import report_generator

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder="static")

db = DatabaseManager()
campaign_mgr = CampaignManager()

TRACKING_PIXEL = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00"
    b"!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01D\x00;"
)

VALID_TEMPLATES = {"facebook", "google", "netflix"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/project-info")
def project_info():
    return render_template("project_info.html")


@app.route("/campaigns", methods=["GET", "POST"])
def campaigns():
    message = None
    if request.method == "POST":
        name = request.form.get("name", "").strip() or "New Campaign"
        template = request.form.get("template", "facebook").strip().lower()
        if template not in VALID_TEMPLATES:
            template = "facebook"
        targets_raw = request.form.get("targets", "").strip()
        targets = [t.strip() for t in targets_raw.replace(";", ",").split(",") if t.strip()]
        if not targets:
            targets = ["demo-target@example.com"]
        created = campaign_mgr.create_campaign(
            name=name,
            template=template,
            targets=targets,
        )
        message = "Campaign created: ID %s — %s" % (created.get("id"), created.get("name"))

    campaigns_list = campaign_mgr.get_all_campaigns()
    return render_template(
        "campaigns.html",
        campaigns=campaigns_list,
        message=message,
        valid_templates=sorted(VALID_TEMPLATES),
    )


@app.route("/credentials")
def credentials():
    records = db.get_all()
    return render_template("credentials.html", records=records)


@app.route("/url-check", methods=["GET", "POST"])
def url_check():
    sample_urls = [
        "https://mailsecure-accounts.example-training.local/signin/challenge",
        "http://192.168.1.55/login/verify",
        "https://accounts.google.com/signin",
        "https://socialconnect-secure-login.example-training.local/session/verify",
        "https://paypa1-security.com/account/confirm",
    ]
    samples = []
    for u in sample_urls:
        try:
            samples.append(detector.analyze_url(u))
        except Exception as e:
            samples.append({"url": u, "risk_level": "high", "reasons": [str(e)]})

    result = None
    checked_url = ""
    if request.method == "POST":
        checked_url = request.form.get("url", "").strip()
        if checked_url:
            try:
                result = detector.analyze_url(checked_url)
            except Exception as e:
                result = {"url": checked_url, "risk_level": "high", "reasons": [str(e)]}

    return render_template(
        "url_check.html",
        samples=samples,
        result=result,
        checked_url=checked_url,
    )


@app.route("/report", methods=["GET", "POST"])
def report():
    report_path = None
    error = None
    if request.method == "POST":
        try:
            report_path = report_generator.generate_report()
        except Exception as e:
            error = str(e)
    return render_template("report.html", report_path=report_path, error=error)


@app.route("/send-email", methods=["GET", "POST"])
def send_email():
    form = {}
    message = None
    error = None

    if request.method == "POST":
        form = {
            "smtp_host": request.form.get("smtp_host", "").strip(),
            "smtp_port": request.form.get("smtp_port", "587").strip(),
            "smtp_user": request.form.get("smtp_user", "").strip(),
            "from_name": request.form.get("from_name", "Security Team").strip(),
            "template": request.form.get("template", "facebook").strip(),
            "campaign_id": request.form.get("campaign_id", "demo-campaign").strip(),
            "base_url": request.form.get("base_url", "http://127.0.0.1:5000").strip(),
            "recipients": request.form.get("recipients", "").strip(),
        }
        smtp_password = request.form.get("smtp_password", "")
        recipients = [e.strip() for e in form["recipients"].replace(";", ",").split(",") if e.strip()]

        if not recipients:
            error = "Please enter at least one recipient email."
        else:
            try:
                ok, errs = send_campaign_emails(
                    smtp_host=form["smtp_host"],
                    smtp_port=form["smtp_port"],
                    smtp_user=form["smtp_user"],
                    smtp_password=smtp_password,
                    from_name=form["from_name"],
                    template_key=form["template"],
                    recipients=recipients,
                    base_url=form["base_url"],
                    campaign_id=form["campaign_id"],
                    use_tls=True,
                )
                message = "Sent %d email(s) successfully." % ok
                if errs:
                    error = "Some failed: " + " | ".join(errs)
            except Exception as e:
                error = str(e)

    return render_template("send_email.html", form=form, message=message, error=error)


@app.route("/phish/<template>/<campaign_id>/<target>")
def phish_page(template, campaign_id, target):
    if template not in VALID_TEMPLATES:
        return "Unknown demo page", 404
    campaign_mgr.record_event(campaign_id, "click")
    return render_template(f"{template}.html", campaign_id=campaign_id, target=target)


@app.route("/track.png/<campaign_id>/<target>")
def track_pixel(campaign_id, target):
    campaign_mgr.record_event(campaign_id, "open")
    return Response(TRACKING_PIXEL, mimetype="image/gif")


@app.route("/login/<template>/<campaign_id>", methods=["POST"])
def capture_credentials(template, campaign_id):
    if template not in VALID_TEMPLATES:
        return "Unknown template", 404

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    hashed_password = SecurityHasher.hash_bcrypt(password)
    ip_address = request.remote_addr
    user_agent = request.headers.get("User-Agent", "")

    db.save_credential(template, username, hashed_password, ip_address, user_agent)
    campaign_mgr.record_event(campaign_id, "submit")
    return redirect(url_for("awareness_page"))


@app.route("/awareness")
def awareness_page():
    return render_template("awareness.html")


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")
