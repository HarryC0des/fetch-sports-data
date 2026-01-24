import json
import os
import time
import requests
from bs4 import BeautifulSoup

GAME_LOG_PATH = "data/game_log.json"
OUTPUT_PATH = "data/game_recap.json"
BASE_URL = "https://www.espn.com/nba/recap/_/gameId/"


def load_game_ids():
    if not os.path.exists(GAME_LOG_PATH):
        raise FileNotFoundError(f"{GAME_LOG_PATH} not found")

    with open(GAME_LOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("gameIds", [])


def fetch_recap_text(game_id, debug=True):
    url = f"{BASE_URL}{game_id}"

    if debug:
        print(f"[DEBUG] Fetching recap for gameId={game_id}")

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    recap_div = soup.find("div", class_="Story__Body t__body")

    if not recap_div:
        print(f"[WARNING] No recap body found for gameId={game_id}")
        return None

    paragraphs = recap_div.find_all("p")
    text_blocks = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]

    if debug:
        print(f"[DEBUG] Extracted {len(text_blocks)} paragraphs for gameId={game_id}")

    return text_blocks


def main():
    os.makedirs("data", exist_ok=True)

    game_ids = load_game_ids()
    print(f"[DEBUG] Loaded {len(game_ids)} game IDs")

    recaps = []

    for game_id in game_ids:
        recap_text = fetch_recap_text(game_id)

        if recap_text:
            recaps.append({
                "gameID": game_id,
                "recapText": recap_text
            })

        # Be polite to ESPN
        time.sleep(1)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(recaps, f, indent=2)

    print(f"[DEBUG] Saved {len(recaps)} recaps to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
