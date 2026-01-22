import json
import re
from datetime import datetime
from collections import Counter
from email.utils import parsedate_to_datetime

# Common English stop words and filler words to exclude
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'was',
    'are', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
    'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
    'as', 'with', 'if', 'from', 'up', 'after', 'before', 'below', 'by', 'out', 'about',
    'there', 'here', 'my', 'his', 'her', 'its', 'your', 'our', 'their', 'as', 'am',
}

def extract_date(pub_date_str):
    """Extract date in YYYY-MM-DD format from pub_date string"""
    try:
        dt = parsedate_to_datetime(pub_date_str)
        return dt.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"[ERROR] Could not parse date '{pub_date_str}': {e}")
        return None

def clean_text(text):
    """Clean text and return list of words"""
    if not text:
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove HTML entities
    text = re.sub(r'&#\d+;', '', text)
    text = re.sub(r'&[a-z]+;', '', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters and numbers, keep only letters and hyphens
    text = re.sub(r'[^a-z\s\-]', '', text)
    
    # Split into words
    words = text.split()
    
    # Filter: remove stop words and short words
    words = [w for w in words if w not in STOP_WORDS and len(w) > 2 and not w.startswith('-')]
    
    return words

def analyze_records():
    """Read records.json and analyze words by date"""
    
    records_file = 'data/records.json'
    
    try:
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {records_file}: {e}")
        return
    
    print(f"[DEBUG] Loaded {len(records)} records")
    
    # Group records by date
    daily_words = {}
    
    for record in records:
        pub_date = record.get('pub_date')
        description = record.get('description', '')
        
        if not pub_date:
            print(f"[WARNING] Record missing pub_date: {record.get('guid', 'unknown')}")
            continue
        
        date_str = extract_date(pub_date)
        if not date_str:
            continue
        
        # Clean and extract words from description
        words = clean_text(description)
        
        if date_str not in daily_words:
            daily_words[date_str] = []
        
        daily_words[date_str].extend(words)
    
    print(f"[DEBUG] Found records for {len(daily_words)} unique dates\n")
    
    # Sort dates and display results
    sorted_dates = sorted(daily_words.keys(), reverse=True)
    
    for date in sorted_dates:
        words = daily_words[date]
        
        if not words:
            print(f"{date}: No words found")
            continue
        
        # Count word frequencies
        word_counts = Counter(words)
        most_common = word_counts.most_common(10)
        
        print(f"{date}:")
        print(f"  Total words: {len(words)} | Unique words: {len(word_counts)}")
        print(f"  Top 10 words:")
        
        for i, (word, count) in enumerate(most_common, 1):
            print(f"    {i:2d}. {word:20s} ({count:3d}x)")
        
        print()

if __name__ == "__main__":
    print("[DEBUG] Starting word analysis by date\n")
    analyze_records()
    print("[DEBUG] Analysis complete")
