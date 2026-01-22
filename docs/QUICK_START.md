# Quick Start Guide

## Running the Web App

### Option 1: Direct Python Execution
```bash
# Navigate to the project directory
cd /workspaces/fetch-sports-data

# Install dependencies
pip install -r requirements.txt

# Start the web server
python web_app.py
```

The app will be available at `http://localhost:5000`

### Option 2: Using the Browser Preview
If you're in a dev container or VS Code:
1. Run `python web_app.py` in the terminal
2. Once you see "Running on http://127.0.0.1:5000", open the Simple Browser
3. Navigate to the localhost URL

## What You'll See

When you open the web app, you'll see:
- **Header**: Title and description
- **Button**: "🔍 Analyze Words by Date"
- **Results Area**: Shows analysis for each date in the records

## How to Use

1. Click the "🔍 Analyze Words by Date" button
2. Wait for the loading spinner (analysis runs)
3. View results organized by date with:
   - Date in readable format (e.g., "Wednesday, January 21, 2026")
   - Total words and unique words counts
   - Top 10 most frequently used words with counts

## Example Results

```
📅 Wednesday, January 21, 2026
Total Words: 81 | Unique Words: 46

#1  trade                 5x
#2  deandre               3x
#3  ayton                 3x
#4  back                  3x
#5  time                  3x
...
```

## Features

✅ Beautiful purple gradient design
✅ Responsive layout for all screen sizes
✅ Real-time loading indicator
✅ Error handling with clear messages
✅ Sorted results by most recent date first
✅ Interactive word cards with hover effects
✅ No page refresh needed - results load dynamically

## Troubleshooting

**"Port 5000 already in use?"**
```bash
# Use a different port
python web_app.py --port 5001
```

**"Module 'flask' not found?"**
```bash
# Install Flask
pip install flask>=2.3.0
```

**"Analysis not showing results?"**
- Check that `data/records.json` exists and has data
- Check browser console for errors (F12)
- Refresh the page and try again
