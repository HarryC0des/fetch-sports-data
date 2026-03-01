# 🏀 Sports Takes Newsletter — Developer README

This repository contains the ingestion, processing, and delivery pipelines for **Sports Takes Newsletter**, an automated system that scrapes NBA data, generates AI-powered sports takes, and delivers personalized emails to users.

This README is intended for **engineers and contributors**.

---

## 📌 Project Overview

**Sports Takes Newsletter** is a data + AI pipeline that:

1. Scrapes NBA game data from ESPN
2. Extracts structured sports facts
3. Generates opinionated sports takes via an LLM
4. Matches takes to user team preferences
5. Sends personalized emails via SendGrid

Key design principles:
- Artifact-based data flow (no raw data committed)
- Low-cost / free-tier LLM usage
- Deterministic personalization logic
- GitHub Actions–driven orchestration

---

## 🧱 Architecture

```
scrapers → artifacts → fact extraction → LLM → takes → email delivery
```

### Key Components

| Component | Responsibility |
|---------|----------------|
| Scrapers | Fetch ESPN NBA data |
| Artifacts | Temporary storage between workflows |
| Fact Extractor | Convert raw text → structured facts |
| LLM Generator | Create sports takes |
| Personalizer | Match takes to users |
| Email Sender | Deliver emails via SendGrid |

---

## 📂 Repository Structure

```
.
├── src/
│   ├── ingest/
│   │   ├── fetch_game_ids.py
│   │   └── fetch_game_recaps.py
│   ├── process/
│   │   ├── extract_facts.py
│   │   ├── generate_takes.py
│   │   └── personalize.py
│   └── delivery/
│       └── send_emails.py
│
├── prompts/
│   ├── versions.json
│   └── v1/
│       ├── base_system.txt
│       ├── output_rules.txt
│       └── styles.json
│
├── .github/
│   └── workflows/
│       ├── ingest.yml
│       ├── generate.yml
│       └── send_emails.yml
│
└── README.md
```

---

## 🔁 Data Flow

### 1. Fetch Game IDs
- Hits ESPN scoreboard API
- Saves game IDs as a **GitHub Actions artifact**
- Output path: `artifacts/game_ids.json`

### 2. Fetch Game Recaps
- Scrapes ESPN recap pages
- Extracts recap text
- Saves output as a **GitHub Actions artifact**
- Output path: `artifacts/recaps.json`

### 2b. Fetch Boxscores
- Scrapes ESPN boxscore pages
- Extracts `div.Card.Card__TableTopBorder` HTML
- Saves output as a **GitHub Actions artifact**
- Output path: `artifacts/boxscores.json`

### 3. Fact Extraction
- Reads recap artifact
- Extracts structured facts
- Outputs new artifact

### 4. LLM Take Generation
- Reads facts artifact
- Optionally uses boxscore artifact text
- Generates takes based on prompt templates
- Outputs takes artifact

### 5. Personalization + Email Delivery
- Matches takes to users
- Renders email templates
- Sends via SendGrid
 - Outputs delivery artifact for audit

---

## 🧠 LLM Integration

### Strategy
- API-based LLM (free-tier preferred)
- Prompts stored externally (config or DB)
- Style applied dynamically per user

### Take Styles
- Factual
- Hot Takes
- Analytical
- Nuanced
- Mix

LLM calls are made **per game**, not per batch, to control token usage.

---

## 📦 Artifacts (Critical Concept)

Artifacts are used to pass data between workflows **without committing to git**.

Example:
- `recaps.json` and `boxscores.json` are generated, uploaded, consumed, and discarded.

Benefits:
- Clean repo
- No large diffs
- Reproducible pipelines

---

## ✉️ Email Delivery

- Provider: SendGrid
- Format: HTML + Plaintext
- Max 3 takes per email
- Skip email if no relevant takes

Unsubscribe handled via SendGrid ASM group (per-user link).

---

## 🔐 Secrets & Configuration

Stored via GitHub Secrets:

- `SENDGRID_API_KEY`
- `SENDGRID_ASM_GROUP_ID`
- `SENDGRID_FROM_EMAIL`
- `SENDGRID_TEMPLATE_ID` (dynamic template ID)
- `NBA_LOGO_BASE_URL` (public base URL for team logos)
- `OPEN_ROUTER_KEY`
- `SUPABASE_KEY`

Other required config:
- `SUPABASE_URL`
- `UNSUBSCRIBE_URL` (optional fallback if ASM is not configured)

Never commit secrets to the repo.

---

## 📊 Observability

### Logging
- Structured logs in GitHub Actions

### Metrics (planned)
- Emails sent
- Takes generated
- LLM failures
- Scrape failures

### Alerts
- Workflow failure notifications

---

## 🚀 Local Development

### Requirements
- Python 3.10+
- pip

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run ingestion locally
```bash
python -m src.ingest.fetch_game_ids
python -m src.ingest.fetch_game_recaps
```

---

## 🗺️ Roadmap

- [x] Fact extraction module
- [x] LLM take generation
- [x] User database integration
- [x] Email scheduling
- [ ] Multi-league support
- [ ] Designed newsletter templates

---

## 🤝 Contributing

- Keep raw data out of git
- Prefer artifacts for intermediate data
- Write idempotent workflows
- Log aggressively

---

## 📄 License

TBD
