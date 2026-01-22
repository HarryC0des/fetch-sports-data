"""
Shared utilities for the sports data project.
"""
import json
import os
import re
from pathlib import Path
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
    'there', 'here', 'my', 'his', 'her', 'its', 'your', 'our', 'their', 'am',
}

# Data directory setup
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
DATA_DIR.mkdir(exist_ok=True)

RECORDS_FILE = DATA_DIR / 'records.json'
RESULTS_FILE = DATA_DIR / 'results.json'
SEEN_GUIDS_FILE = DATA_DIR / 'seen_guids.txt'


def load_json(filepath, default=None):
    """
    Load JSON file safely.
    
    Args:
        filepath: Path to JSON file
        default: Default value if file doesn't exist or is invalid
        
    Returns:
        Parsed JSON or default value
    """
    filepath = Path(filepath)
    try:
        if filepath.exists() and filepath.stat().st_size > 0:
            return json.loads(filepath.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, ValueError, OSError) as e:
        print(f"[WARNING] Could not load {filepath}: {e}")
    
    return default if default is not None else []


def save_json(filepath, data):
    """
    Save data to JSON file.
    
    Args:
        filepath: Path to save JSON file
        data: Data to save
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding='utf-8')


def load_records(filepath=None):
    """Load records from JSON file."""
    filepath = filepath or RECORDS_FILE
    return load_json(filepath, [])


def save_records(records, filepath=None):
    """Save records to JSON file."""
    filepath = filepath or RECORDS_FILE
    save_json(filepath, records)


def load_results(filepath=None):
    """Load results from JSON file."""
    filepath = filepath or RESULTS_FILE
    return load_json(filepath, [])


def save_results(results, filepath=None):
    """Save results to JSON file."""
    filepath = filepath or RESULTS_FILE
    save_json(filepath, results)


def load_seen_guids(filepath=None):
    """Load set of seen GUIDs from file."""
    filepath = filepath or SEEN_GUIDS_FILE
    try:
        if Path(filepath).exists() and Path(filepath).stat().st_size > 0:
            return set(Path(filepath).read_text(encoding='utf-8').splitlines())
    except (ValueError, OSError):
        pass
    return set()


def save_seen_guids(guids, filepath=None):
    """Save set of seen GUIDs to file."""
    filepath = filepath or SEEN_GUIDS_FILE
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    Path(filepath).write_text('\n'.join(sorted(guids)), encoding='utf-8')


def extract_date(pub_date_str):
    """
    Extract date in YYYY-MM-DD format from pub_date string.
    
    Args:
        pub_date_str: Publication date string (e.g., "Wed, 21 Jan 2026 14:35:39 +0000")
        
    Returns:
        Date string in YYYY-MM-DD format or None
    """
    try:
        dt = parsedate_to_datetime(pub_date_str)
        return dt.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"[ERROR] Could not parse date '{pub_date_str}': {e}")
        return None


def clean_text(text):
    """
    Clean text and return list of words.
    Removes HTML entities, URLs, emails, special characters.
    Filters out stop words and short words.
    
    Args:
        text: Text to clean
        
    Returns:
        List of cleaned words
    """
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


def analyze_text_by_date(descriptions_by_date):
    """
    Analyze word frequencies grouped by date.
    
    Args:
        descriptions_by_date: Dict mapping date -> list of descriptions
        
    Returns:
        Dict mapping date -> {total_words, unique_words, top_10}
    """
    result = {}
    
    for date, descriptions in descriptions_by_date.items():
        all_words = []
        
        for description in descriptions:
            words = clean_text(description)
            all_words.extend(words)
        
        if not all_words:
            result[date] = {
                'total_words': 0,
                'unique_words': 0,
                'top_10': []
            }
            continue
        
        word_counts = Counter(all_words)
        most_common = word_counts.most_common(10)
        
        result[date] = {
            'total_words': len(all_words),
            'unique_words': len(word_counts),
            'top_10': [{'word': word, 'count': count} for word, count in most_common]
        }
    
    return result
