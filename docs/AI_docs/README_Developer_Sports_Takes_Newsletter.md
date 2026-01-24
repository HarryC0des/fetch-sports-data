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
│   ├── fetch_game_ids.py
│   ├── fetch_game_recaps.py
│   ├── extract_facts.py        # (planned)
│   ├── generate_takes.py       # (planned)
│   └── send_emails.py          # (planned)
│
├── data/
│   └── game_log.json           # Game IDs only
│
├── .github/
│   └── workflows/
│       ├── fetch-game-ids.yml
│       ├── fetch-game-recaps.yml
│       ├── generate-takes.yml  # (planned)
│       └── send-emails.yml     # (planned)
│
└── README.md
```

---

## 🔁 Data Flow

### 1. Fetch Game IDs
- Hits ESPN scoreboard API
- Stores game IDs in `data/game_log.json`
- Commits file to repo

### 2. Fetch Game Recaps
- Scrapes ESPN recap pages
- Extracts recap text
- Saves output as a **GitHub Actions artifact**
- Output path: `/tmp/game_recap.json`

### 3. Fact Extraction (Planned)
- Reads recap artifact
- Extracts structured facts
- Outputs new artifact

### 4. LLM Take Generation (Planned)
- Reads facts artifact
- Generates takes based on prompt templates
- Stores takes in database or artifact

### 5. Email Delivery (Planned)
- Matches takes to users
- Renders email templates
- Sends via SendGrid

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
- `game_recap.json` is generated, uploaded, consumed, and discarded.

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

Unsubscribe handled via footer link.

---

## 🔐 Secrets & Configuration

Stored via GitHub Secrets:

- `SENDGRID_API_KEY`
- `LLM_API_KEY` (provider-specific)

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
pip install requests beautifulsoup4
```

### Run scraper locally
```bash
python src/fetch_game_recaps.py
```

---

## 🗺️ Roadmap

- [ ] Fact extraction module
- [ ] LLM take generation
- [ ] User database integration
- [ ] Email scheduling
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
