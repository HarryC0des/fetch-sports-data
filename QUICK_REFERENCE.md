# Quick Reference Guide

## 📁 File Locations

### Core Modules (in `src/`)
| Module | Purpose | Key Functions |
|--------|---------|---|
| `utils.py` | Shared utilities | `load_records()`, `save_records()`, `clean_text()`, `analyze_text_by_date()` |
| `rss_fetcher.py` | Fetch news | `fetch_rss()`, `fetch_and_store()` |
| `ai_generator.py` | Generate takes | `generate_take()`, `generate_take_from_content()` |
| `analyzer.py` | Analyze words | `analyze_records_by_date()`, `print_analysis_results()` |

### Entry Points

#### CLI Scripts (in `scripts/`)
```bash
python -m scripts.fetch_rss              # Fetch RSS
python -m scripts.generate_take          # Generate AI takes
python -m scripts.analyze_words          # Analyze words
```

#### Main Pipeline
```bash
python main.py                           # Full pipeline
python main.py --fetch-only              # Fetch only
python main.py --generate-only           # Generate only
python main.py --analyze-only            # Analyze only
```

#### Web Application
```bash
python web/app.py                        # Start web server
# Visit http://localhost:5000
```

### Web Application (in `web/`)
| File | Purpose |
|------|---------|
| `app.py` | Flask routes & API endpoints |
| `templates/index.html` | Web UI |

## 🔌 API Endpoints

### Web API
```
GET /                    - Main page
GET /api/analyze        - Run analysis (returns JSON)
```

### Response Format
```json
{
  "success": true,
  "data": {
    "2026-01-21": {
      "total_words": 81,
      "unique_words": 46,
      "top_10": [
        {"word": "trade", "count": 5},
        ...
      ]
    }
  }
}
```

## 📚 Data Files

### Records
```
data/records.json       - Fetched articles (title, description, content, etc.)
data/seen_guids.txt     - Tracking for duplicates
```

### Results
```
results.json           - Generated takes (guid, take, original_title, etc.)
```

## ⚙️ Configuration

### Environment Variables
```bash
OPEN_ROUTER_KEY=your-api-key   # Required for AI generation
```

### File Paths (Automatic)
- Data directory: `data/`
- Records file: `data/records.json`
- Results file: `data/results.json`
- Seen GUIDs: `data/seen_guids.txt`

## 🔄 Data Flow

```
RSS Feed
  ↓
[src/rss_fetcher.py]
  → Fetch & parse RSS
  → Check for duplicates
  → Save to data/records.json
  ↓
[src/ai_generator.py]
  → Load records
  → Generate AI takes
  → Save to results.json
  ↓
[src/analyzer.py]
  → Load records
  → Group by date
  → Analyze word frequencies
  → Return results
```

## 🐍 Python Usage Examples

### Fetch
```python
from src.rss_fetcher import fetch_and_store
count = fetch_and_store()
print(f"Added {count} new items")
```

### Generate
```python
from src.ai_generator import generate_take
generate_take()
```

### Analyze
```python
from src.analyzer import analyze_records_by_date, print_analysis_results
results = analyze_records_by_date()
print_analysis_results(results)
```

### Load Data
```python
from src.utils import load_records, load_results
records = load_records()
results = load_results()
```

## 🧹 Common Tasks

### Clear Data
```bash
rm data/records.json data/seen_guids.txt data/results.json
```

### View Records
```python
from src.utils import load_records
import json
records = load_records()
print(json.dumps(records[0], indent=2))
```

### View Results
```python
from src.utils import load_results
import json
results = load_results()
print(json.dumps(results[0], indent=2))
```

### Test Imports
```bash
python -c "from src.utils import load_records; print(f'OK: {len(load_records())} records')"
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'src'` | Run from project root: `cd /path/to/fetch-sports-data` |
| No records found | Run `python -m scripts.fetch_rss` first |
| `OPEN_ROUTER_KEY not set` | Export: `export OPEN_ROUTER_KEY="your-key"` |
| Web app won't start | Install Flask: `pip install flask` |
| Import errors in scripts | Run: `pip install -r requirements.txt` |

## 📖 Documentation

| Doc | Content |
|-----|---------|
| `README.md` | Overview & quick start |
| `REORGANIZATION_SUMMARY.md` | What changed |
| `docs/ARCHITECTURE.md` | Design & structure |
| `docs/MIGRATION.md` | Migration guide |
| `docs/QUICK_START.md` | Getting started |

## 🚀 Common Workflows

### Full Pipeline (Fetch → Generate → Analyze)
```bash
python main.py
```

### Fetch Only
```bash
python main.py --fetch-only
# OR
python -m scripts.fetch_rss
```

### Generate Only
```bash
python main.py --generate-only
# OR
python -m scripts.generate_take
```

### Analyze Only
```bash
python main.py --analyze-only
# OR
python -m scripts.analyze_words
```

### Web Interface
```bash
python web/app.py
# Then open http://localhost:5000
```

### GitHub Actions (Automated)
- Runs every 3 hours
- Fetches RSS → Generates takes → Commits
- See `.github/workflows/ai_bot.yml`

## 📊 Module Dependencies

```
main.py
├── src.rss_fetcher
│   └── src.utils
├── src.ai_generator
│   └── src.utils
├── src.analyzer
│   └── src.utils
└── (scripts use same structure)

web/app.py
└── src.analyzer
    └── src.utils
```

## ✅ Verification Checklist

- [x] All modules import correctly
- [x] All CLI scripts work
- [x] Data persists correctly
- [x] Analysis produces accurate results
- [x] Web app loads successfully
- [x] GitHub Actions compatible
- [x] Documentation complete
- [x] File references updated
