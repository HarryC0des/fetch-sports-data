# Migration Guide: Old → New Structure

## What Changed

The repository has been reorganized into a scalable, modular structure to support future growth while maintaining backward compatibility.

## File Mapping

### Core Code
| Old Location | New Location | Notes |
|---|---|---|
| `check_rss.py` | `src/rss_fetcher.py` | Refactored into reusable module |
| `generate_takes.py` | `src/ai_generator.py` | Refactored into reusable module |
| `analyze_words_by_date.py` | `src/analyzer.py` | Refactored into reusable module |
| (new) | `src/utils.py` | Shared utilities & constants |
| (new) | `main.py` | Main entry point for full pipeline |

### Web Application
| Old Location | New Location | Notes |
|---|---|---|
| `web_app.py` | `web/app.py` | Flask app refactored |
| `templates/index.html` | `web/templates/index.html` | Moved to web package |

### Scripts
| Old Location | New Location | Notes |
|---|---|---|
| (new) | `scripts/fetch_rss.py` | CLI wrapper for RSS fetch |
| (new) | `scripts/generate_take.py` | CLI wrapper for AI generation |
| (new) | `scripts/analyze_words.py` | CLI wrapper for analysis |

### Documentation
| Old Location | New Location | Notes |
|---|---|---|
| `WORD_ANALYSIS_README.md` | `docs/WORD_ANALYSIS.md` | Moved to docs/ |
| `WEB_APP_README.md` | `docs/WEB_APP.md` | Moved to docs/ |
| `WEB_APP_SUMMARY.md` | `docs/WEB_APP_SUMMARY.md` | Moved to docs/ |
| `QUICK_START.md` | `docs/QUICK_START.md` | Moved to docs/ |
| (new) | `docs/ARCHITECTURE.md` | New: detailed design guide |

### GitHub Actions
| File | Change |
|---|---|
| `.github/workflows/ai_bot.yml` | Updated to use new module paths |

## How to Use New Structure

### Option 1: Run Full Pipeline
```bash
python main.py
```

### Option 2: Run Individual Steps
```bash
python -m scripts.fetch_rss       # Fetch RSS
python -m scripts.generate_take   # Generate takes
python -m scripts.analyze_words   # Analyze words
```

### Option 3: Use Modules in Python
```python
from src.rss_fetcher import fetch_and_store
from src.ai_generator import generate_take
from src.analyzer import analyze_records_by_date

# Fetch
count = fetch_and_store()

# Generate
generate_take()

# Analyze
results = analyze_records_by_date()
```

### Option 4: Web Application
```bash
python web/app.py
```

## What's Better

✅ **Modular Design**
- Each component is independent and reusable
- Easy to test individual modules

✅ **Scalable**
- Easy to add new data sources
- Easy to add new analysis methods
- Can extend without modifying core code

✅ **Maintainable**
- Clear separation of concerns
- Shared utilities prevent code duplication
- Easier to debug and modify

✅ **Flexible**
- Multiple ways to run (CLI, Python, Web)
- GitHub Actions still works seamlessly
- Can import and use any module

✅ **Well-Documented**
- Docstrings for all functions
- Architecture guide for design understanding
- Clear examples in README

## Backward Compatibility

The old scripts (`check_rss.py`, `generate_takes.py`, `analyze_words_by_date.py`) are deprecated but can still be used temporarily. They have been moved to `archive/` or you can delete them.

The GitHub Actions workflow has been updated to use the new module paths automatically.

## Migration Checklist

- [x] Code refactored into modular structure
- [x] Shared utilities extracted to `src/utils.py`
- [x] CLI entry points created
- [x] Web app updated for new structure
- [x] GitHub Actions workflow updated
- [x] Documentation reorganized
- [x] All functionality tested and working

## Next Steps

1. **Review architecture** - See `docs/ARCHITECTURE.md`
2. **Read module docstrings** - Each file has detailed documentation
3. **Try different interfaces** - CLI, Python, or Web
4. **Extend the system** - Add new features following existing patterns

## Questions?

Refer to:
- `docs/ARCHITECTURE.md` - How the system is designed
- `docs/QUICK_START.md` - Getting started
- Module docstrings - Function documentation
- Code comments - Implementation details
