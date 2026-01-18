import requests
import xml.etree.ElementTree as ET
import json
from pathlib import Path
from datetime import datetime

RSS_URL = "https://sports.yahoo.com/nba/news/rss"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

RECORDS_FILE = DATA_DIR / "records.json"
SEEN_FILE = DATA_DIR / "seen_guids.txt"

# Load existing data
try:
    records = json.loads(RECORDS_FILE.read_text()) if RECORDS_FILE.exists() and RECORDS_FILE.stat().st_size > 0 else []
except (json.JSONDecodeError, ValueError):
    records = []
try:
    seen_guids = set(SEEN_FILE.read_text().splitlines()) if SEEN_FILE.exists() and SEEN_FILE.stat().st_size > 0 else set()
except (ValueError, OSError):
    seen_guids = set()

# RSS namespaces
NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/"
}

# Fetch RSS
resp = requests.get(RSS_URL, timeout=30)
resp.raise_for_status()

root = ET.fromstring(resp.text)

# Get latest 5 items
items = root.findall("./channel/item")[:5]

new_records = []

for item in items:
    guid = item.findtext("guid")
    if not guid or guid in seen_guids:
        continue

    record = {
        "guid": guid,
        "title": item.findtext("title", "").strip(),
        "link": item.findtext("link"),
        "description": item.findtext("description", "").strip(),
        "content_html": item.findtext("content:encoded", namespaces=NS),
        "author": item.findtext("dc:creator", namespaces=NS),
        "publisher": item.findtext("dc:publisher", namespaces=NS),
        "source": item.findtext("source"),
        "pub_date": item.findtext("pubDate"),
        "ingested_at": datetime.utcnow().isoformat() + "Z",
    }

    new_records.append(record)
    seen_guids.add(guid)

if new_records:
    records.extend(new_records)

    RECORDS_FILE.write_text(
        json.dumps(records, indent=2, ensure_ascii=False)
    )
    SEEN_FILE.write_text("\n".join(sorted(seen_guids)))

    print(f"Added {len(new_records)} new items.")
else:
    print("No new items found.")
