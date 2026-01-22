# Sports Data Fetch & Analysis

Automated pipeline to fetch sports news, generate AI-powered analysis takes, and analyze word frequencies.

## Features

✨ **Complete Pipeline**
- Fetch latest sports news from RSS feeds
- Generate AI-powered sports takes using OpenRouter API
- Analyze word frequencies from descriptions
- Web UI for interactive analysis

🏗️ **Scalable Architecture**
- Modular design with clear separation of concerns
- Reusable utilities for data operations
- Easy to add new data sources or analysis methods
- CLI + Web interfaces for flexibility

📊 **Data Management**
- Automatic duplicate detection
- JSON-based data persistence
- Efficient word frequency analysis with stop word filtering

## Quick Start

### Installation

```bash
# Clone and install
pip install -r requirements.txt
```

### Run Complete Pipeline

```bash
python main.py
```

This will:
1. Fetch latest sports news from RSS
2. Generate AI takes for new articles
3. Analyze word frequencies by date

### Run Individual Steps

```bash
python -m scripts.fetch_rss          # Fetch RSS only
python -m scripts.generate_take      # Generate takes only
python -m scripts.analyze_words      # Analyze words only
```

### Web Interface

```bash
python web/app.py
# Visit http://localhost:5000
```

## Project Structure

```
src/                    # Core modules
├── utils.py           # Shared utilities
├── rss_fetcher.py     # RSS fetching
├── ai_generator.py    # AI takes generation
└── analyzer.py        # Word analysis

web/                    # Flask web app
├── app.py             # Routes & API
└── templates/         # HTML templates

scripts/               # CLI entry points
├── fetch_rss.py
├── generate_take.py
└── analyze_words.py

data/                  # Data storage
├── records.json       # Fetched articles
├── seen_guids.txt     # Tracking
└── results.json       # Generated takes

docs/                  # Documentation
├── ARCHITECTURE.md    # Design guide
├── QUICK_START.md
├── WORD_ANALYSIS.md
└── WEB_APP.md
```

## Configuration

### Environment Variables

```bash
OPEN_ROUTER_KEY=your_api_key_here
```

For local development, create a `.env` file or export the variable:
```bash
export OPEN_ROUTER_KEY="your-api-key"
```

For GitHub Actions, add the secret:
- Go to Settings → Secrets and variables → Actions
- Add `OPEN_ROUTER_KEY` secret

## Architecture

For detailed architecture and design decisions, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

Key points:
- **Modular design** - Each component is independent
- **Reusable utilities** - `src/utils.py` handles common operations
- **Scalable** - Easy to add new features without breaking existing code
- **Well-documented** - Each module has docstrings and type hints

## Usage Examples

### Fetch News
```python
from src.rss_fetcher import fetch_and_store
count = fetch_and_store()
```

### Generate Takes
```python
from src.ai_generator import generate_take
generate_take()
```

### Analyze Words
```python
from src.analyzer import analyze_records_by_date
results = analyze_records_by_date()
```

## Automation

GitHub Actions workflow runs automatically:
- **Schedule**: Every 3 hours (configurable in `.github/workflows/ai_bot.yml`)
- **Steps**: Fetch RSS → Generate takes → Commit changes
- **Trigger**: Can also run manually via "Run workflow"

## Extending the Project

### Add New Data Source
1. Create `src/new_fetcher.py` following `rss_fetcher.py` pattern
2. Use `save_records()` from `src/utils.py`
3. Add CLI wrapper in `scripts/`
4. Update `main.py` pipeline

### Add New Analysis
1. Create `src/new_analyzer.py`
2. Load records with `load_records()`
3. Return results in consistent format
4. Add to web app or CLI

### Extend Web App
1. Add route to `web/app.py`
2. Create template in `web/templates/`
3. Import analysis functions from `src/`

## Dependencies

- **requests** - HTTP for RSS & API calls
- **flask** - Web framework
- Python 3.6+ (built-in libraries for data processing)

## Troubleshooting

**OPEN_ROUTER_KEY not set**
```bash
export OPEN_ROUTER_KEY="your-api-key"
```

**No records found**
- Run `python -m scripts.fetch_rss` first
- Check `data/records.json` exists

**Analysis shows no results**
- Check records have `pub_date` field
- Verify `description` field is populated

**Web app won't start**
```bash
pip install flask
python web/app.py
```

## Support & Contributing

- See docs/ for detailed guides
- Check existing modules for code patterns
- All functions include docstrings

## License

[Your License Here]

## Author

HarryC0des

Repository to build and test workflows to grab and analyze sports or other information from RSS feeds.
