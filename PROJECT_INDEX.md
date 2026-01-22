# Project Index & Navigation Guide

## 📍 Start Here

1. **First Time?** → Read [`README.md`](README.md)
2. **Want to Understand the Design?** → Read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
3. **Just Want to Run It?** → Read [`docs/QUICK_START.md`](docs/QUICK_START.md)
4. **Migrating from Old Structure?** → Read [`docs/MIGRATION.md`](docs/MIGRATION.md)

## 📚 Documentation Index

### Getting Started
- [`README.md`](README.md) - Project overview, features, quick start
- [`docs/QUICK_START.md`](docs/QUICK_START.md) - Installation & basic usage
- [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) - Command reference & examples

### Architecture & Design
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - **Complete design guide** - Read this for deep understanding
- [`docs/MIGRATION.md`](docs/MIGRATION.md) - Migration from old structure
- [`REORGANIZATION_SUMMARY.md`](REORGANIZATION_SUMMARY.md) - What changed and why

### Feature Documentation
- [`docs/WORD_ANALYSIS.md`](docs/WORD_ANALYSIS.md) - Word frequency analysis guide
- [`docs/WEB_APP.md`](docs/WEB_APP.md) - Web application guide
- [`docs/WEB_APP_SUMMARY.md`](docs/WEB_APP_SUMMARY.md) - Web app quick summary

## 🗂️ Directory Map

### Source Code (`src/`)
Core application modules - These do the actual work.

```
src/
├── __init__.py
├── utils.py             ← Start here for shared utilities
├── rss_fetcher.py       ← RSS feed operations
├── ai_generator.py      ← AI take generation
└── analyzer.py          ← Word frequency analysis
```

**Use them:**
```python
from src.rss_fetcher import fetch_and_store
from src.ai_generator import generate_take
from src.analyzer import analyze_records_by_date
from src.utils import load_records, save_records
```

### CLI Scripts (`scripts/`)
Command-line entry points - Run from terminal.

```
scripts/
├── __init__.py
├── fetch_rss.py         ← Fetch RSS news
├── generate_take.py     ← Generate AI takes
└── analyze_words.py     ← Analyze word frequencies
```

**Run them:**
```bash
python -m scripts.fetch_rss
python -m scripts.generate_take
python -m scripts.analyze_words
```

### Web Application (`web/`)
Flask web app with UI.

```
web/
├── __init__.py
├── app.py               ← Flask routes & API
└── templates/
    └── index.html       ← Web UI
```

**Run it:**
```bash
python web/app.py
```

### Data (`data/`)
Where information is stored.

```
data/
├── records.json         ← Fetched articles
├── seen_guids.txt       ← Duplicate tracking
└── seen_ids.txt         ← Legacy tracking
```

### Documentation (`docs/`)
Everything you need to know.

```
docs/
├── ARCHITECTURE.md      ← Design & structure guide
├── MIGRATION.md         ← Upgrade from old version
├── QUICK_START.md       ← Getting started
├── WORD_ANALYSIS.md     ← Analysis feature docs
├── WEB_APP.md          ← Web application docs
└── WEB_APP_SUMMARY.md  ← Web app summary
```

### Configuration
```
.github/
└── workflows/
    └── ai_bot.yml       ← GitHub Actions automation
```

## 🚀 Quick Command Reference

### Run Entire Pipeline
```bash
python main.py
```

### Run Specific Steps
```bash
python main.py --fetch-only      # Just fetch
python main.py --generate-only   # Just generate takes
python main.py --analyze-only    # Just analyze words
```

### Use CLI Scripts
```bash
python -m scripts.fetch_rss
python -m scripts.generate_take
python -m scripts.analyze_words
```

### Start Web App
```bash
python web/app.py
# Visit http://localhost:5000
```

### Use Modules in Python
```python
from src.analyzer import analyze_records_by_date
results = analyze_records_by_date()
```

## 🔍 Finding What You Need

### Want to...
| Goal | Go To |
|------|-------|
| Understand the overall design | `docs/ARCHITECTURE.md` |
| Run the entire system | `README.md` + `python main.py` |
| Fetch RSS news | `scripts/fetch_rss.py` |
| Generate AI takes | `scripts/generate_take.py` |
| Analyze word frequencies | `scripts/analyze_words.py` |
| Use web interface | `web/app.py` + http://localhost:5000 |
| Add new data source | `docs/ARCHITECTURE.md` + see examples |
| Add new analysis | `docs/ARCHITECTURE.md` + create in `src/` |
| Extend web app | `web/app.py` + `web/templates/` |
| Understand data flow | `docs/ARCHITECTURE.md` |
| See what changed | `REORGANIZATION_SUMMARY.md` |
| Migrate from old version | `docs/MIGRATION.md` |
| Quick reference | `QUICK_REFERENCE.md` |

## 📊 System Overview

```
┌─────────────────────────────────────────────────┐
│            Sports Data Pipeline                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  RSS Feed → [rss_fetcher] → data/records.json   │
│            ↓                                     │
│  Records → [ai_generator] → data/results.json   │
│            ↓                                     │
│  Records → [analyzer] → Display/API             │
│                                                  │
├─────────────────────────────────────────────────┤
│  Entry Points:                                   │
│  • python main.py (orchestrates all)            │
│  • python -m scripts.* (individual steps)       │
│  • python web/app.py (web interface)            │
│  • .github/workflows/ai_bot.yml (automation)    │
├─────────────────────────────────────────────────┤
│  Core Module: src/utils.py                      │
│  (shared utilities, file I/O, text processing)  │
└─────────────────────────────────────────────────┘
```

## ✅ Verification Checklist

Ensure everything works:

```bash
# Test imports
python -c "from src import utils, rss_fetcher, ai_generator, analyzer; print('✅ Imports OK')"

# Test analyzer
python -m scripts.analyze_words

# Test main
python main.py --analyze-only

# Test web (in separate terminal)
python web/app.py
```

## 🔗 Cross-References

- **Need to understand a function?** → Check module docstrings
- **Want to add a feature?** → See `docs/ARCHITECTURE.md` → "Extending the Project"
- **Something broken?** → Check `QUICK_REFERENCE.md` → "Troubleshooting"
- **Not sure where a file is?** → Use this index with Ctrl+F

## 📝 Module Quick Links

### `src/utils.py`
**Functions:** `load_records()`, `save_records()`, `clean_text()`, `extract_date()`, `analyze_text_by_date()`
**Use when:** Loading data, cleaning text, analyzing words

### `src/rss_fetcher.py`
**Functions:** `fetch_rss()`, `fetch_and_store()`, `process_feed_items()`
**Use when:** Getting news from RSS feeds

### `src/ai_generator.py`
**Functions:** `generate_take()`, `generate_take_from_content()`
**Use when:** Generating AI takes from articles

### `src/analyzer.py`
**Functions:** `analyze_records_by_date()`, `print_analysis_results()`
**Use when:** Analyzing word frequencies

### `web/app.py`
**Routes:** `GET /`, `GET /api/analyze`
**Use when:** Running web interface

## 🎓 Learning Path

1. **Start** → Read `README.md`
2. **Install** → Follow `docs/QUICK_START.md`
3. **Understand** → Read `docs/ARCHITECTURE.md`
4. **Explore** → Try different entry points
5. **Extend** → See "Extending the Project" in `docs/ARCHITECTURE.md`

## 📞 Support Resources

- **Getting started?** → `README.md`
- **Command reference?** → `QUICK_REFERENCE.md`
- **Architecture questions?** → `docs/ARCHITECTURE.md`
- **Code examples?** → Module docstrings
- **Troubleshooting?** → `QUICK_REFERENCE.md` troubleshooting section
