#!/usr/bin/env python3
"""
CLI Script: Analyze Word Frequencies by Date

Usage:
    python -m scripts.analyze_words
"""
from src.analyzer import analyze_records_by_date, print_analysis_results

if __name__ == "__main__":
    print("[INFO] Starting word analysis...")
    results = analyze_records_by_date()
    print_analysis_results(results)
    print("[INFO] Analysis complete.")
