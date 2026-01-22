"""
RSS Feed Fetcher Module

Fetches sports news from RSS feeds and stores them in JSON format.
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from html.parser import HTMLParser
from src.utils import load_records, save_records, load_seen_guids, save_seen_guids


RSS_URL = "https://sports.yahoo.com/nba/news/rss"

# RSS namespaces
NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/"
}


class HTMLToPlainText(HTMLParser):
    """Convert HTML content to plain text."""
    
    def __init__(self):
        super().__init__()
        self.text = []
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_text(self):
        return ''.join(self.text).strip()


def strip_html(html_content):
    """
    Strip HTML tags and return plain text.
    
    Args:
        html_content: HTML string
        
    Returns:
        Plain text content or None
    """
    if not html_content:
        return None
    parser = HTMLToPlainText()
    parser.feed(html_content)
    return parser.get_text()


def fetch_rss(url=None, max_items=5):
    """
    Fetch RSS feed from URL.
    
    Args:
        url: RSS feed URL (uses default if not provided)
        max_items: Maximum number of items to fetch
        
    Returns:
        List of parsed items
    """
    url = url or RSS_URL
    print(f"[DEBUG] Fetching RSS from: {url}")
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        print(f"[DEBUG] RSS fetch successful (status: {resp.status_code})")
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch RSS: {e}")
        return []
    
    try:
        root = ET.fromstring(resp.text)
        items = root.findall("./channel/item")[:max_items]
        print(f"[DEBUG] Found {len(items)} items in RSS feed")
        return items
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse RSS XML: {e}")
        return []


def process_feed_items(items):
    """
    Process RSS items and return new records.
    
    Args:
        items: List of RSS items from ElementTree
        
    Returns:
        List of new record dictionaries
    """
    print(f"[DEBUG] Processing {len(items)} RSS items")
    
    # Load existing data
    records = load_records()
    seen_guids = load_seen_guids()
    existing_guids = set(record["guid"] for record in records[:5])
    
    new_records = []
    
    for item in items:
        guid = item.findtext("guid")
        if not guid:
            print(f"[WARNING] Item missing GUID, skipping")
            continue
        
        # Check if it's a new item
        if guid in seen_guids and guid in existing_guids:
            print(f"[DEBUG] Skipping seen GUID: {guid}")
            continue
        
        record = {
            "guid": guid,
            "title": item.findtext("title", "").strip(),
            "link": item.findtext("link"),
            "description": item.findtext("description", "").strip(),
            "content_html": strip_html(item.findtext("content:encoded", namespaces=NS)),
            "author": item.findtext("dc:creator", namespaces=NS),
            "publisher": item.findtext("dc:publisher", namespaces=NS),
            "source": item.findtext("source"),
            "pub_date": item.findtext("pubDate"),
            "ingested_at": datetime.utcnow().isoformat() + "Z",
        }
        
        new_records.append(record)
        seen_guids.add(guid)
        print(f"[DEBUG] Processed new item: {record['title'][:50]}...")
    
    return new_records, seen_guids, records


def fetch_and_store(url=None, max_items=5):
    """
    Fetch RSS feed and store new items.
    
    Args:
        url: RSS feed URL
        max_items: Maximum items to fetch
        
    Returns:
        Number of new items added
    """
    items = fetch_rss(url, max_items)
    if not items:
        print("[WARNING] No items to process")
        return 0
    
    new_records, seen_guids, records = process_feed_items(items)
    
    if new_records:
        records = new_records + records
        save_records(records)
        save_seen_guids(seen_guids)
        print(f"[SUCCESS] Added {len(new_records)} new items")
        return len(new_records)
    else:
        print("[DEBUG] No new items found")
        return 0
