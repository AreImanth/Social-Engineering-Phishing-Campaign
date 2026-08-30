"""
anti_phishing/detector.py

Heuristic analysis of URLs/domains for common phishing indicators:
  - Raw IP address used as the host instead of a domain name
  - Excessive subdomains ("mimicry" via long lookalike subdomains)
  - Suspicious keywords often used in phishing domains
  - Brand-name mimicry (e.g. "paypa1" instead of "paypal")
  - Use of URL shorteners
  - Non-standard TLDs commonly abused in phishing campaigns

This module only ever analyzes strings you pass to it -- it does not
fetch, browse, or interact with the URLs in any way.
"""

import re
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
    "verify", "secure", "update", "confirm", "signin", "login",
    "account", "billing", "suspended", "urgent", "reset",
]

KNOWN_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd"}

# A small illustrative set of well-known brand names to check for
# lookalike/typosquat patterns against. Not exhaustive -- for teaching only.
PROTECTED_BRANDS = ["paypal", "google", "microsoft", "apple", "amazon", "netflix", "facebook", "bank"]

SUSPICIOUS_TLDS = {".xyz", ".top", ".club", ".gq", ".tk", ".ml", ".zip", ".mov"}

IP_PATTERN = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")


def _looks_like_typosquat(hostname: str) -> str | None:
    """Very simple check: brand name present but with digit substitutions
    or as a lookalike subdomain rather than the actual registered domain."""
    lowered = hostname.lower()
    for brand in PROTECTED_BRANDS:
        # character-substitution typosquat, e.g. paypa1, g00gle
        leet = brand.replace("o", "0").replace("l", "1").replace("i", "1")
        if leet in lowered and brand not in lowered:
            return brand
        # brand name present but not as the actual registrable domain
        # (heuristic: brand appears, but hostname has extra hyphenated segments)
        if brand in lowered and "-" in lowered and not lowered.startswith(brand + "."):
            return brand
    return None


def analyze_url(url: str) -> dict:
    """
    Analyze a single URL and return a dict:
      { "risk_level": "low"|"medium"|"high", "reasons": [...] }
    """
    reasons = []
    try:
        parsed = urlparse(url if "://" in url else f"http://{url}")
    except ValueError:
        return {"risk_level": "high", "reasons": ["URL could not be parsed"]}

    hostname = parsed.hostname or ""
    scheme = parsed.scheme

    if scheme != "https":
        reasons.append("Not using HTTPS")

    if IP_PATTERN.match(hostname):
        reasons.append("Host is a raw IP address rather than a domain name")

    subdomain_count = max(hostname.count("."), 0)
    if subdomain_count >= 3:
        reasons.append(f"Unusually many subdomain levels ({subdomain_count})")

    for kw in SUSPICIOUS_KEYWORDS:
        if kw in hostname.lower():
            reasons.append(f"Suspicious keyword in hostname: '{kw}'")
            break  # one mention is enough to flag

    if hostname.lower() in KNOWN_SHORTENERS:
        reasons.append("Known URL-shortening service (destination is hidden)")

    for tld in SUSPICIOUS_TLDS:
        if hostname.lower().endswith(tld):
            reasons.append(f"Uncommon/high-abuse top-level domain: '{tld}'")
            break

    typosquat_brand = _looks_like_typosquat(hostname)
    if typosquat_brand:
        reasons.append(f"Possible typosquat/mimicry of brand '{typosquat_brand}'")

    # Risk scoring
    if typosquat_brand or IP_PATTERN.match(hostname):
        risk_level = "high"
    elif len(reasons) >= 2:
        risk_level = "medium"
    elif reasons:
        risk_level = "low"
    else:
        risk_level = "low"
        reasons.append("No obvious red flags detected")

    return {"url": url, "risk_level": risk_level, "reasons": reasons}


def analyze_batch(urls: list) -> list:
    """Analyze a list of URLs, returning a list of result dicts."""
    return [analyze_url(u) for u in urls]


if __name__ == "__main__":
    samples = [
        "https://accounts.google.com/signin",
        "http://192.168.0.5/login/verify",
        "https://paypa1-security-update.com/confirm",
        "https://bit.ly/3xample",
        "https://mail.suspicious-billing-verify.top",
    ]
    for result in analyze_batch(samples):
        print(f"{result['url']}\n  risk: {result['risk_level']}\n  reasons: {result['reasons']}\n")
