# Social Engineering Phishing Campaign Tool

A Flask-based phishing campaign simulation and awareness platform designed for **IT administrators, security professionals, and organizations** that need to assess employee security posture, run internal phishing simulations, and deliver targeted awareness training. Equally suited for large enterprises, educational institutes, government agencies, and any team that wants to demonstrate realistic phishing campaigns in a controlled, ethical environment.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.3-red.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Table of Contents

- [Overview](#overview)
- [Who Is This For](#who-is-this-for)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage — Web Interface](#usage--web-interface)
- [Usage — CLI Dashboard](#usage--cli-dashboard)
- [Core Modules](#core-modules)
- [Testing](#testing)
- [Ethical Use & Compliance](#ethical-use--compliance)
- [Status](#Status)
- [Contributions](#Contributions)
- [License](#license)

---

## Overview

The **Social Engineering Phishing Campaign Tool** is a self-hosted, local-first platform for running simulated phishing campaigns and measuring how targets (employees, students, team members) respond. It provides:

- Realistic mock login pages modeled after widely-used services (Facebook, Google, Netflix)
- A full campaign lifecycle pipeline: **sent → opened → clicked → submitted**
- Credential capture with **bcrypt hashing** — a demonstration of what attackers do, used here for awareness and forensics training
- An **anti-phishing URL heuristic analyzer** that security teams can use to screen suspicious links before including them in campaigns or allowing them through email gateways
- **SMTP integration** to send campaign emails through your organization's mail server or any SMTP provider
- A **CLI dashboard** and a **PDF report generator** for post-campaign analysis and reporting to management

Everything runs locally. No external services are contacted without your explicit configuration. No real credentials leave the machine in plaintext.

---

## Who Is This For

| Role | How they use it |
|---|---|
| **IT Administrators / Security Teams** | Plan and execute internal phishing simulation campaigns against employee inboxes. Track open/click/submit rates. Generate PDF reports for security awareness metrics and management review. |
| **Security Awareness Trainers** | Demonstrate real-looking phishing pages to a group, then debrief with the awareness page and the anti-phishing URL checker. Show firsthand how convincing a fake login can look. |
| **SOC / Incident Response Teams** | Use the URL heuristic detector as a lightweight triage tool when evaluating suspicious links from emails or tickets. |
| **Educational Institutes / Universities** | Run phishing simulations for faculty, staff, and student bodies as part of cybersecurity awareness programs. |
| **Consultants / Pentesters (authorized)** | Demonstrate phishing risk to clients in a controlled, consented, and scoped engagement. |
| **Anyone wanting to demonstrate phishing campaigns** | A self-contained stack you can spin up locally and use to show how phishing works — and how to spot it. |

---

## Features

| Feature | Description |
|---|---|
| **Mock phishing pages** | Facebook, Google, and Netflix styled login clones served by Flask. Each page includes an embedded tracking pixel and submits credentials to the server for capture and hashing. |
| **Campaign lifecycle tracking** | Sent, opened (via tracking pixel), clicked (page view), and submitted (credential form POST) are recorded per target email and visible in the dashboard, web UI, and PDF report. |
| **Credential capture with bcrypt** | Submitted usernames and passwords are hashed with **bcrypt** and stored in `data/captured_credentials.json`. No plaintext passwords are persisted. This demonstrates how attackers capture credentials; in a real engagement all target emails must be owned by or authorized by the organization. |
| **Anti-phishing URL detector** | Heuristic analysis of URLs for raw IP hosts, excessive subdomains, suspicious keywords, known URL shorteners, high-abuse TLDs, and brand-name typosquatting patterns. Returns a risk level (**low / medium / high**) plus the specific reasons. The detector never fetches or browses the URLs — it only inspects the strings you pass to it. |
| **SMTP email sending** | Build and send campaign emails via any SMTP server (Gmail) with TLS support. Three built-in email templates (Facebook security alert, Google sign-in alert, Netflix account update) with brand-styled HTML bodies. |
| **Interactive CLI dashboard** | 5-option menu for security operators: view campaign metrics, view captured credentials, run URL heuristics against sample or custom URLs, generate PDF report, exit. |
| **PDF report generation** | ReportLab-based report with campaign metrics table, captured credentials table, and key-takeaways section — suitable for sharing with management or including in awareness program documentation. |

---

## Project Structure

```
socail_engine_working/
│
├── main.py                      # Unified entry point — starts Flask server
│                                 # in a background thread and launches the
│                                 # interactive CLI dashboard.
├── requirements.txt             # Flask, reportlab, bcrypt, tabulate
├── LICENSE                      # MIT license
│
├── server/                      # Flask application
│   ├── __init__.py
│   ├── app.py                   # All Flask routes
│   ├── email_sender.py          # SMTP email dispatch for campaign messages
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── index.html            # Landing page
│   │   ├── campaigns.html        # Campaign creation / metrics UI
│   │   ├── credentials.html      # View captured credential records
│   │   ├── url_check.html        # Interactive anti-phishing URL checker
│   │   ├── report.html           # Trigger PDF report generation
│   │   ├── send_email.html       # SMTP configuration form
│   │   ├── facebook.html         # Mock Facebook login clone
│   │   ├── google.html           # Mock Google login clone
│   │   ├── netflix.html          # Mock Netflix login clone
│   │   └── awareness.html        # Post-simulation red-flags training page
│
├── core/                        # Core engine modules
│   ├── __init__.py
│   ├── campaign.py              # Campaign lifecycle manager (JSON-backed,
│   │                              thread-safe, file-persisted)
│   ├── database.py              # Credentials database manager (JSON-backed,
│   │                              thread-safe, bcrypt hashes only)
│   ├── hashing.py               # SecurityHasher: MD5, SHA-256, bcrypt
│   └── tracker.py               # Tracking-pixel and event emulation helpers
│
├── gui/                         # Operator console and reporting
│   ├── __init__.py
│   ├── dashboard.py             # Interactive CLI menu (5 options)
│   └── report_generator.py      # ReportLab PDF report compiler
│
├── anti_phishing/               # Defensive URL heuristic module
│   ├── __init__.py
│   └── detector.py              # analyze_url() / analyze_batch() — fully
│                                 # functional, never fetches or browses URLs
│
├── tests/
│   └── test_simulator.py        # Unit tests (17 tests)
│
└── data/                        # populated when a campaign is created and populated with data.
    ├── captured_credentials.json # credential records
    ├── campaign_state.json      # campaign metrics state
    └── campaign_report.pdf      # PDF report output
```

---

## Prerequisites

- **Python 3.8** or later
- **pip** (or **uv**) for installing dependencies
- An **SMTP server** (optional — only needed if you want to actually send campaign emails; the demo pages, tracking pixel, and credential capture all work without it)

---

## Installation

1. Navigate to the project folder:

   ```bash
   cd /path/to/socail_engine_working
   ```

2. (Recommended) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate        # On Windows
   # source venv/bin/activate   # On macOS / Linux
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Or with uv:

   ```bash
   uv pip install -r requirements.txt
   ```

---

## Quick Start

Run the unified entry point:

```bash
python main.py
```

This will:

1. Start the Flask demo server in a background daemon thread on `http://127.0.0.1:5000`
2. Open the default browser to the index page
3. Drop you into the interactive CLI dashboard menu

From the browser you can visit the mock login pages, create campaigns, check URLs, and trigger reports. From the CLI dashboard you can view metrics, inspect the credential database, run URL checks, and generate reports.

---

## Usage — Web Interface

The Flask app exposes the following routes:

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Landing page with links to demo pages and navigation to all other sections. |
| `GET` | `/campaigns` | View all campaigns and their metrics. |
| `POST` | `/campaigns` | Create a new campaign (name, template, comma/semicolon-separated target emails). |
| `GET` | `/credentials` | View all captured credential records (hashed passwords, timestamps, IPs, user agents). |
| `GET` | `/url-check` | Interactive anti-phishing URL checker with precomputed sample results. |
| `POST` | `/url-check` | Submit a URL to analyze. |
| `GET` | `/report` | Trigger PDF report generation. |
| `POST` | `/report` | Generate and download the report. |
| `GET` | `/send-email` | SMTP configuration form for sending campaign emails. |
| `POST` | `/send-email` | Send campaign emails via configured SMTP. |
| `GET` | `/phish/<template>/<campaign_id>/<target>` | Serve the mock login page for the given template (`facebook` / `google` / `netflix`), record a "clicked" event. |
| `GET` | `/track.png/<campaign_id>/<target>` | Serve a 1x1 tracking pixel GIF, record an "opened" event. |
| `POST` | `/login/<template>/<campaign_id>` | Accept credential form submission, hash the password with bcrypt, store the record, record a "submitted" event, redirect to awareness page. |
| `GET` | `/awareness` | Post-simulation training page explaining red flags. |

---

## Usage — CLI Dashboard

The interactive menu (launched by `main.py` or directly via `gui/dashboard.py`) provides:

| Option | Action |
|---|---|
| `[1]` | **View campaign metrics** — Table of all campaigns with columns: Campaign ID, Name, Targets, Sent, Opened, Clicked, Submitted. |
| `[2]` | **View captured credentials database** — All stored credential records: ID, Template, Username/Target, Password Hash (truncated), Timestamp. Includes a note that passwords are bcrypt hashes — no plaintext is stored. |
| `[3]` | **Run anti-phishing URL heuristics** — Runs the detector against a hardcoded set of sample URLs and displays the risk level and reasons for each. |
| `[4]` | **Generate PDF report** — Calls `gui/report_generator.py` to produce `data/campaign_report.pdf`. |
| `[5]` | **Exit** — Closes the dashboard. |

---

## Core Modules

### `server/app.py`

Central Flask application. Defines all routes listed above. Uses `CampaignManager` and `DatabaseManager` from `core/` for persistence, `SecurityHasher` from `core/hashing.py` for password hashing, and the `anti_phishing/detector.py` module for URL analysis.

### `server/email_sender.py`

`send_campaign_emails()` — constructs and sends HTML email messages using `smtplib`. Supports TLS and `SMTP_SSL`. Three built-in templates (`facebook`, `google`, `netflix`) with brand-styled HTML bodies.

### `core/campaign.py` — `CampaignManager`

File-backed (JSON) campaign lifecycle tracker with thread-safe read/write via `threading.Lock`. Supports:

- `create_campaign(campaign_id, name, template, targets)`
- `get_campaign(campaign_id)`
- `get_all_campaigns()`
- `record_event(campaign_id, target_or_event, event_type=None)` — accepts two signatures:
  - `record_event(cid, "click" | "open" | "submit" | "sent")`
  - `record_event(cid, target_email, "clicked" | "opened" | "submitted" | "sent")`

State is persisted in `data/campaign_state.json`.

### `core/database.py` — `DatabaseManager`

Thread-safe (`RLock`) JSON-backed credential store. Only stores hashed values (never plaintext). Key method:

- `save_credential(template, username, password_hash, ip_address, user_agent)`

Data lives in `data/captured_credentials.json`.

### `core/hashing.py` — `SecurityHasher`

Static utility class providing:

| Method | Description |
|---|---|
| `hash_md5(password)` | MD5 hex digest |
| `hash_sha256(password)` | SHA-256 hex digest |
| `hash_bcrypt(password)` | bcrypt hash (with auto-generated salt) |
| `verify_bcrypt(password, hashed)` | Boolean verification |

bcrypt is the primary hash used for credential storage; MD5 and SHA-256 are available for demonstration / comparison purposes.

### `core/tracker.py`

Emulates email dispatch tracking (no real email is sent by this module) and holds the raw bytes of a 1x1 transparent GIF used as the tracking pixel served at `/track.png/<campaign_id>/<target>`.

### `anti_phishing/detector.py`

This is under active development and will be added once completed, in general it would be working in this manner:

- `analyze_url(url)` → `{"url": ..., "risk_level": ..., "reasons": [...]}`
- `analyze_batch(urls)` → list of `analyze_url` results

Flags checked:

- Raw IP address used as host
- Excessive subdomain nesting
- Suspicious keywords (`verify`, `secure`, `confirm`, `signin`, `login`, `account`, `billing`, `suspended`, `urgent`, `reset`)
- Known URL shorteners (`bit.ly`, `tinyurl.com`, `t.co`, `goo.gl`, `ow.ly`, `is.gd`)
- High-abuse TLDs (`.xyz`, `.top`, `.club`, `.gq`, `.tk`, `.ml`, `.zip`, `.mov`)
- Brand-name typosquatting patterns (e.g. `paypa1`)

### `gui/dashboard.py`

Interactive CLI menu loop (see [Usage — CLI Dashboard](#usage--cli-dashboard)). Pulls data from `CampaignManager` and `DatabaseManager`, delegates URL checks to `detector.analyze_url()`, and triggers PDF generation via `report_generator.generate_report()`.

### `gui/report_generator.py`

`generate_report()` — builds a PDF (campaign metrics table, credentials table, key takeaways) using ReportLab and writes it to `data/campaign_report.pdf`. Returns the file path.

### `data/seed_data.py`

Populates the system with fictional data:

- 6 fictional targets at `@classroom-demo.local`
- 6 fabricated sample password strings
- A demo campaign ("Q3 Classroom Awareness Exercise") with pre-seeded sent/opened/clicked/submitted events
- Sample credential records for every other target (hashed with bcrypt via `SecurityHasher`)

Run once before a demo:

```bash
python data/seed_data.py
```

---

## Ethical Use & Compliance

> **This tool is designed for authorized security awareness and assessment purposes only.**

- **Only target people who are part of your organization or who have given explicit consent.** Phishing simulations should be run against employees, students, or team members as part of an approved awareness program — never against strangers, the general public, or anyone who has not opted in.
- **Get organizational approval.** Before launching campaigns against real employee inboxes, ensure you have the proper authorization from management, HR, legal, or your security governance team. Document the scope, timing, and target population.
- **Use owned or authorized target emails.** The credential capture feature stores bcrypt hashes, but in a real engagement you must only target addresses owned by or explicitly authorized by your organization. Do not target personal email addresses without consent.
- **Be transparent with participants.** Inform employees or students that phishing simulations are part of the security awareness program. After a campaign, use the awareness page and the debrief to explain the red flags rather than punishing participants.
- **The mock login pages mimic real services for training realism** (Facebook, Google, Netflix). They are **not affiliated with or endorsed** by those companies. Do not use these templates to impersonate real services outside of a consented, scoped training exercise.
- **Do not use this tool to target real users without their explicit knowledge and consent.** This is a training and assessment tool — not a stealth attack platform.
- **Handle captured data responsibly.** Credential hashes are stored locally in `data/captured_credentials.json`. Treat this file as sensitive. Restrict access, back it up securely, and delete it when it is no longer needed for reporting or training purposes.
- **Comply with applicable laws and policies.** Depending on your jurisdiction and organization, phishing simulations may be subject to data protection regulations, employee privacy laws, and internal IT policy. Consult your legal and compliance teams before deploying.

---

## Status

The tool is under active development where i would be adding more templates and make them more convincing, and also will work on the url analyzer.

---

## Contributions

Contributions are appreciated and welcomed, please fork me for contributions or collaborations :) 

---

## License

MIT License — see the [LICENSE](LICENSE) file in the project root.
