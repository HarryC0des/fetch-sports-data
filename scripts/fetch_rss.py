#!/usr/bin/env python3
"""
CLI Script: Fetch Sports News RSS Feed

Usage:
    python -m scripts.fetch_rss
"""
from src.rss_fetcher import fetch_and_store

if __name__ == "__main__":
    print("[INFO] Starting RSS fetch...")
    count = fetch_and_store()
    print(f"[INFO] Fetch complete. {count} new items added.")
