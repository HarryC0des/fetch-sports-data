# Word Analysis Script

## Overview
`analyze_words_by_date.py` reads the `description` field from `records.json` and analyzes the most frequently used words for each unique date found in the `pub_date` field.

## Features
- Groups articles by publication date (YYYY-MM-DD format)
- Extracts and cleans text (removes HTML entities, URLs, email addresses, special characters)
- Filters out common English stop words and filler words
- Only includes words with 3+ characters to focus on meaningful terms
- Shows top 10 most frequently used words for each date
- Displays word count statistics (total and unique words per day)

## Usage
```bash
python analyze_words_by_date.py
```

## Output
For each date in the records, the script outputs:
- Date (YYYY-MM-DD)
- Total and unique word counts
- Top 10 words with their frequencies

## Example Output
```
2026-01-21:
  Total words: 81 | Unique words: 46
  Top 10 words:
     1. trade                (  5x)
     2. deandre              (  3x)
     3. ayton                (  3x)
     ...
```

## Stop Words Excluded
The script filters out common English words like: the, a, an, and, or, but, in, on, at, to, for, is, was, are, be, trade-specific filler words, pronouns, and more.
