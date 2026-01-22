from flask import Flask, render_template, jsonify
import json
import re
from datetime import datetime
from collections import Counter
from email.utils import parsedate_to_datetime

app = Flask(__name__)

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

def extract_date(pub_date_str):
    """Extract date in YYYY-MM-DD format from pub_date string"""
    try:
        dt = parsedate_to_datetime(pub_date_str)
        return dt.strftime('%Y-%m-%d')
    except Exception as e:
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
        return {'error': f'Failed to load records: {str(e)}'}
    
    # Group records by date
    daily_words = {}
    
    for record in records:
        pub_date = record.get('pub_date')
        description = record.get('description', '')
        
        if not pub_date:
            continue
        
        date_str = extract_date(pub_date)
        if not date_str:
            continue
        
        # Clean and extract words from description
        words = clean_text(description)
        
        if date_str not in daily_words:
            daily_words[date_str] = []
        
        daily_words[date_str].extend(words)
    
    # Build result
    result = {}
    sorted_dates = sorted(daily_words.keys(), reverse=True)
    
    for date in sorted_dates:
        words = daily_words[date]
        
        if not words:
            result[date] = {
                'total_words': 0,
                'unique_words': 0,
                'top_10': []
            }
            continue
        
        # Count word frequencies
        word_counts = Counter(words)
        most_common = word_counts.most_common(10)
        
        result[date] = {
            'total_words': len(words),
            'unique_words': len(word_counts),
            'top_10': [{'word': word, 'count': count} for word, count in most_common]
        }
    
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['GET'])
def api_analyze():
    """API endpoint to run analysis and return results"""
    try:
        results = analyze_records()
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
