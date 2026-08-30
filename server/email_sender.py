import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


EMAIL_TEMPLATES = {
    "facebook": {
        "subject": "Security Alert: Unusual login attempt on your Facebook account",
        "html": """
        <div style="font-family: Arial, sans-serif; max-width: 560px; margin: 0 auto; color: #1c1e21;">
          <div style="background:#1877f2; color:#fff; padding:16px 20px; font-size:20px; font-weight:bold;">
            Facebook
          </div>
          <div style="padding:24px 20px; border:1px solid #ddd; border-top:none;">
            <p>Hi,</p>
            <p>We detected an unusual login attempt on your Facebook account from a new device or location.</p>
            <p>If this was you, you can safely ignore this message. If not, please review your account activity immediately.</p>
            <p style="text-align:center; margin:28px 0;">
              <a href="{link}" style="background:#1877f2; color:#fff; padding:12px 24px; text-decoration:none; border-radius:6px; font-weight:bold;">
                Review Account Activity
              </a>
            </p>
            <p style="color:#65676b; font-size:13px;">This is an automated security message from Facebook.</p>
          </div>
        </div>
        """,
    },
    "google": {
        "subject": "Security alert: New sign-in on your Google Account",
        "html": """
        <div style="font-family: 'Google Sans', Arial, sans-serif; max-width: 560px; margin: 0 auto; color: #202124;">
          <div style="padding:20px; border-bottom:1px solid #dadce0;">
            <span style="font-size:22px; font-weight:500; color:#4285f4;">Google</span>
          </div>
          <div style="padding:24px 20px;">
            <p>Hi,</p>
            <p>A new sign-in to your Google Account was detected. If this was you, no further action is required.</p>
            <p>If you don't recognize this activity, secure your account now.</p>
            <p style="text-align:center; margin:28px 0;">
              <a href="{link}" style="background:#1a73e8; color:#fff; padding:12px 24px; text-decoration:none; border-radius:4px; font-weight:500;">
                Check Activity
              </a>
            </p>
            <p style="color:#5f6368; font-size:13px;">You received this email to let you know about important changes to your Google Account.</p>
          </div>
        </div>
        """,
    },
    "netflix": {
        "subject": "Important: Update required on your Netflix account",
        "html": """
        <div style="font-family: Arial, sans-serif; max-width: 560px; margin: 0 auto; color: #221f1f; background:#fff;">
          <div style="background:#e50914; color:#fff; padding:16px 20px; font-size:22px; font-weight:bold; letter-spacing:1px;">
            NETFLIX
          </div>
          <div style="padding:24px 20px; border:1px solid #ddd; border-top:none;">
            <p>Hi,</p>
            <p>We need you to confirm some account details to keep your Netflix membership active and avoid service interruption.</p>
            <p>Please review your account within 24 hours.</p>
            <p style="text-align:center; margin:28px 0;">
              <a href="{link}" style="background:#e50914; color:#fff; padding:12px 28px; text-decoration:none; border-radius:4px; font-weight:bold;">
                Review Account
              </a>
            </p>
            <p style="color:#666; font-size:13px;">— The Netflix Team</p>
          </div>
        </div>
        """,
    },
}


def send_campaign_emails(
    smtp_host,
    smtp_port,
    smtp_user,
    smtp_password,
    from_name,
    template_key,
    recipients,
    base_url,
    campaign_id,
    use_tls=True,
):
    """
    Send simulated security emails.
    Returns (success_count, errors_list).
    """
    if template_key not in EMAIL_TEMPLATES:
        raise ValueError("Unknown template: %s" % template_key)

    tmpl = EMAIL_TEMPLATES[template_key]
    success = 0
    errors = []

    for email in recipients:
        link = "%s/phish/%s/%s/%s" % (base_url.rstrip("/"), template_key, campaign_id, email)
        html_body = tmpl["html"].format(link=link)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = tmpl["subject"]
        msg["From"] = "%s <%s>" % (from_name, smtp_user)
        msg["To"] = email
        msg.attach(MIMEText(html_body, "html"))

        try:
            if use_tls:
                server = smtplib.SMTP(smtp_host, int(smtp_port), timeout=30)
                server.ehlo()
                server.starttls()
                server.ehlo()
            else:
                server = smtplib.SMTP_SSL(smtp_host, int(smtp_port), timeout=30)

            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [email], msg.as_string())
            server.quit()
            success += 1
        except Exception as e:
            errors.append("%s → %s" % (email, str(e)))

    return success, errors