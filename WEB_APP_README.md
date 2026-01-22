# Web App - Word Analysis Viewer

## Overview
A Flask-based web application that provides an interactive interface for viewing word frequency analysis from sports news articles.

## Features
- Beautiful, responsive web interface
- Click a button to analyze word frequencies
- Results grouped by publication date
- Shows top 10 most used words per date
- Word count statistics (total and unique words)
- Real-time loading feedback
- Error handling with user-friendly messages

## Installation

1. Install Flask:
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install flask
```

## Usage

1. Start the web server:
```bash
python web_app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Click the "🔍 Analyze Words by Date" button to run the analysis

## How It Works

- **Frontend**: Interactive HTML/CSS/JavaScript interface
- **Backend**: Flask server with API endpoint `/api/analyze`
- **Analysis**: Same logic as `analyze_words_by_date.py`
- **Output**: Displays results organized by date with word frequencies

## API Endpoint

`GET /api/analyze`

Returns JSON with structure:
```json
{
  "success": true,
  "data": {
    "2026-01-21": {
      "total_words": 81,
      "unique_words": 46,
      "top_10": [
        {"word": "trade", "count": 5},
        {"word": "deandre", "count": 3},
        ...
      ]
    }
  }
}
```

## File Structure
```
/templates/
  └── index.html       # Main web interface
web_app.py            # Flask application
```

## Stop Words
The analysis filters out 100+ common English stop words and filler words to focus on meaningful terms (nouns, names, key concepts).

## Notes
- The app uses the same stop words filter as the CLI script
- Words shorter than 3 characters are excluded
- All analysis is done in real-time when you click the button
