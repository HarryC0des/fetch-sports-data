"""
Word Frequency Analysis Module

Analyzes word frequencies in sports news grouped by publication date.
"""
from src.utils import load_records, extract_date, analyze_text_by_date


def analyze_records_by_date():
    """
    Analyze word frequencies from records grouped by publication date.
    
    Returns:
        Dict mapping date -> {total_words, unique_words, top_10}
    """
    print("[DEBUG] Starting word analysis by date")
    
    records = load_records()
    print(f"[DEBUG] Loaded {len(records)} records")
    
    # Group descriptions by date
    daily_descriptions = {}
    
    for record in records:
        pub_date = record.get('pub_date')
        description = record.get('description', '')
        
        if not pub_date:
            print(f"[WARNING] Record missing pub_date: {record.get('guid', 'unknown')}")
            continue
        
        date_str = extract_date(pub_date)
        if not date_str:
            continue
        
        if date_str not in daily_descriptions:
            daily_descriptions[date_str] = []
        
        daily_descriptions[date_str].append(description)
    
    print(f"[DEBUG] Found records for {len(daily_descriptions)} unique dates")
    
    # Analyze word frequencies
    results = analyze_text_by_date(daily_descriptions)
    
    # Sort by date (most recent first)
    sorted_results = {date: results[date] for date in sorted(results.keys(), reverse=True)}
    
    return sorted_results


def print_analysis_results(results):
    """
    Print analysis results to console in readable format.
    
    Args:
        results: Dict of analysis results from analyze_records_by_date()
    """
    print("[DEBUG] Analysis Results:\n")
    
    for date, analysis in results.items():
        print(f"{date}:")
        print(f"  Total words: {analysis['total_words']} | Unique words: {analysis['unique_words']}")
        print(f"  Top 10 words:")
        
        for i, item in enumerate(analysis['top_10'], 1):
            print(f"    {i:2d}. {item['word']:20s} ({item['count']:3d}x)")
        
        print()


if __name__ == "__main__":
    print("[DEBUG] Starting analysis...")
    results = analyze_records_by_date()
    print_analysis_results(results)
    print("[DEBUG] Analysis complete")
