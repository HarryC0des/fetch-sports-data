#!/usr/bin/env python3
"""
Sports Data Fetch & Analysis - Main Entry Point

This script orchestrates the complete pipeline:
1. Fetch latest sports news from RSS
2. Generate AI-powered sports takes
3. Analyze word frequencies

Usage:
    python main.py                  # Run full pipeline
    python main.py --fetch-only     # Fetch RSS only
    python main.py --generate-only  # Generate takes only
    python main.py --analyze-only   # Analyze words only
"""
import sys
import argparse
from src.rss_fetcher import fetch_and_store
from src.ai_generator import generate_take
from src.analyzer import analyze_records_by_date, print_analysis_results


def run_pipeline():
    """Run the complete pipeline: fetch -> generate -> analyze."""
    print("[INFO] ====== Starting Sports Data Pipeline ======\n")
    
    print("[STEP 1/3] Fetching RSS Feed...")
    count = fetch_and_store()
    print(f"[STEP 1/3] ✓ RSS fetch complete. {count} new items added.\n")
    
    print("[STEP 2/3] Generating AI Takes...")
    generate_take()
    print("[STEP 2/3] ✓ Take generation complete.\n")
    
    print("[STEP 3/3] Analyzing Word Frequencies...")
    results = analyze_records_by_date()
    print(f"[STEP 3/3] ✓ Analysis complete for {len(results)} dates.\n")
    
    print("[INFO] ====== Pipeline Completed Successfully ======\n")


def fetch_only():
    """Run fetch step only."""
    print("[INFO] Running RSS fetch only...\n")
    count = fetch_and_store()
    print(f"[INFO] ✓ Complete. {count} new items added.")


def generate_only():
    """Run generate step only."""
    print("[INFO] Running take generation only...\n")
    generate_take()
    print("[INFO] ✓ Generation complete.")


def analyze_only():
    """Run analysis step only."""
    print("[INFO] Running word analysis only...\n")
    results = analyze_records_by_date()
    print_analysis_results(results)
    print("[INFO] ✓ Analysis complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Sports Data Fetch & Analysis Pipeline",
        epilog="For more info, see docs/README.md"
    )
    
    parser.add_argument(
        '--fetch-only',
        action='store_true',
        help='Run RSS fetch step only'
    )
    parser.add_argument(
        '--generate-only',
        action='store_true',
        help='Run take generation step only'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Run word analysis step only'
    )
    
    args = parser.parse_args()
    
    try:
        if args.fetch_only:
            fetch_only()
        elif args.generate_only:
            generate_only()
        elif args.analyze_only:
            analyze_only()
        else:
            run_pipeline()
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
