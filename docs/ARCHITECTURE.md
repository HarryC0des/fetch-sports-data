# Architecture Guide

## Project Structure

```
fetch-sports-data/
├── src/                          # Core application modules
│   ├── __init__.py
│   ├── utils.py                  # Shared utilities & constants
│   ├── rss_fetcher.py            # RSS feed fetching & processing
│   ├── ai_generator.py           # AI take generation
│   └── analyzer.py               # Word frequency analysis
│
├── web/                          # Flask web application
│   ├── __init__.py
│   ├── app.py                    # Flask app & routes
│   └── templates/
│       └── index.html            # Web UI
│
├── scripts/                      # CLI entry points
│   ├── fetch_rss.py             # RSS fetch command
│   ├── generate_take.py         # Take generation command
│   └── analyze_words.py         # Analysis command
│
├── data/                         # Data files
│   ├── records.json             # Fetched articles
│   ├── seen_guids.txt           # Tracking
│   └── .gitkeep
│
├── docs/                         # Documentation
│   ├── QUICK_START.md
│   ├── WORD_ANALYSIS.md
│   ├── WEB_APP.md
│   ├── WEB_APP_SUMMARY.md
│   └── ARCHITECTURE.md           # This file
│
├── .github/
│   └── workflows/
│       └── ai_bot.yml            # GitHub Actions workflow
│
├── main.py                       # Pipeline entry point
├── requirements.txt              # Dependencies
└── README.md                     # Project overview
```

## Module Overview

### `src/utils.py`
**Shared utilities and constants**

Key functions:
- `load_json()` / `save_json()` - JSON file I/O
- `load_records()` / `save_records()` - Record management
- `load_results()` / `save_results()` - Results management
- `load_seen_guids()` / `save_seen_guids()` - Tracking seen articles
- `extract_date()` - Parse publication dates
- `clean_text()` - Text cleaning & word extraction
- `analyze_text_by_date()` - Word frequency analysis

Constants:
- `STOP_WORDS` - 100+ common English words to exclude
- `PROJECT_ROOT` - Project directory
- `DATA_DIR` - Data storage directory
- File paths for records, results, seen GUIDs

### `src/rss_fetcher.py`
**RSS feed fetching and processing**

Key functions:
- `fetch_rss()` - Fetch RSS feed from URL
- `process_feed_items()` - Parse RSS items
- `fetch_and_store()` - Complete fetch & store pipeline

Features:
- HTML to plain text conversion
- Duplicate detection
- Automatic data persistence
- Comprehensive logging

### `src/ai_generator.py`
**AI-powered sports takes generation**

Key functions:
- `generate_take_from_content()` - Call OpenRouter API
- `generate_take()` - Full generation pipeline

Features:
- OpenRouter API integration
- Error handling & fallbacks
- Duplicate avoidance (checks GUIDs)
- Detailed logging

API Configuration:
- Endpoint: `https://openrouter.ai/api/v1/chat/completions`
- Model: `openai/gpt-4-turbo`
- API Key: `OPEN_ROUTER_KEY` environment variable

### `src/analyzer.py`
**Word frequency analysis**

Key functions:
- `analyze_records_by_date()` - Analyze by publication date
- `print_analysis_results()` - Format results for display

Features:
- Groups articles by date
- Counts word frequencies
- Excludes stop words
- Returns top 10 words per date

### `web/app.py`
**Flask web application**

Routes:
- `GET /` - Main index page
- `GET /api/analyze` - Run analysis (returns JSON)

Features:
- Beautiful responsive UI
- Real-time analysis
- Error handling
- Loading indicators

## Data Flow

### RSS Fetch Pipeline
```
fetch_rss()
  → Parse RSS XML
  → Extract items
  ↓
process_feed_items()
  → Load existing records & seen GUIDs
  → Check for duplicates
  → Create record objects
  ↓
store results
  → Save to data/records.json
  → Update data/seen_guids.txt
```

### Take Generation Pipeline
```
generate_take()
  → Load records from data/records.json
  → Load results from data/results.json
  → Compare most recent GUIDs
  ↓
If new article found:
  → Extract content_html
  → Call OpenRouter API
  → Parse response
  ↓
save result
  → Create result object
  → Save to data/results.json
```

### Analysis Pipeline
```
analyze_records_by_date()
  → Load records
  → Extract publication dates
  → Group descriptions by date
  ↓
analyze_text_by_date()
  → For each date:
    → Clean text (remove stop words, etc.)
    → Count word frequencies
    → Get top 10 words
  ↓
Return results
  → date → {total_words, unique_words, top_10}
```

## Scalability Design

The architecture supports future growth:

### Adding New Data Sources
1. Create new fetcher in `src/` (e.g., `twitter_fetcher.py`)
2. Reuse `utils.save_records()` for consistency
3. Add CLI wrapper in `scripts/`
4. Update `main.py` to include new pipeline step

### Adding New Analysis Methods
1. Create analyzer in `src/` (e.g., `sentiment_analyzer.py`)
2. Reuse `utils.load_records()` and file I/O
3. Follow same function signature pattern
4. Add to web app routes as needed

### Extending Web App
1. Add new routes to `web/app.py`
2. Create new templates in `web/templates/`
3. Reuse existing utilities for data operations
4. Keep analysis logic in `src/` modules

### Adding New APIs/Services
1. Create service module in `src/` (e.g., `slack_notifier.py`)
2. Store credentials in environment variables
3. Follow error handling patterns from `ai_generator.py`
4. Integrate into pipeline steps as needed

## Configuration

### Environment Variables
```bash
OPEN_ROUTER_KEY         # OpenRouter API key for AI generation
```

### File Paths (auto-configured in utils.py)
```
data/records.json       # Fetched articles
results.json           # Generated takes
data/seen_guids.txt    # Tracking
```

## Running the System

### Complete Pipeline
```bash
python main.py
```

### Individual Steps
```bash
python -m scripts.fetch_rss      # Fetch only
python -m scripts.generate_take  # Generate only
python -m scripts.analyze_words  # Analyze only
```

### Web Application
```bash
python web/app.py
# Visit http://localhost:5000
```

## Dependencies

Core:
- `requests` - HTTP requests
- `flask` - Web framework

Built-in:
- `json` - Data serialization
- `re` - Text processing
- `xml.etree` - RSS parsing
- `collections` - Word counting
- `email.utils` - Date parsing

## Testing & Development

### Adding Tests
Create `tests/` directory with:
- `test_utils.py`
- `test_rss_fetcher.py`
- `test_ai_generator.py`
- `test_analyzer.py`

### Adding New Features
1. Create module in `src/`
2. Write functions following existing patterns
3. Reuse utilities from `src/utils.py`
4. Add CLI wrapper if needed
5. Update documentation

### Debugging
- All modules include `[DEBUG]` and `[ERROR]` logging
- Check `data/` directory for intermediate files
- Review individual module docstrings
