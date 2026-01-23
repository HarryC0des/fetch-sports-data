import requests
import json

URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

def fetch_game_ids(debug=True):
    if debug:
        print("[DEBUG] Starting fetch_game_ids()")
        print(f"[DEBUG] Target URL: {URL}")

    # Step 1: Make the HTTP request
    try:
        response = requests.get(URL, timeout=10)
        if debug:
            print(f"[DEBUG] HTTP status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return []

    # Step 2: Validate response
    if response.status_code != 200:
        print("[ERROR] Non-200 response received")
        return []

    # Step 3: Parse JSON
    try:
        data = response.json()
        if debug:
            print("[DEBUG] JSON parsed successfully")
            print(f"[DEBUG] Top-level keys: {list(data.keys())}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON: {e}")
        return []

    # Step 4: Extract events
    events = data.get("events")

    if events is None:
        print("[ERROR] 'events' key not found in response")
        return []

    if debug:
        print(f"[DEBUG] Number of events found: {len(events)}")

    # Step 5: Extract game IDs
    game_ids = []

    for index, event in enumerate(events):
        if debug:
            print(f"[DEBUG] Processing event #{index}")

        game_id = event.get("id")

        if game_id:
            if debug:
                print(f"[DEBUG] Found game ID: {game_id}")
            game_ids.append(game_id)
        else:
            print(f"[WARNING] Event #{index} missing 'id' field")

    if debug:
        print(f"[DEBUG] Total game IDs collected: {len(game_ids)}")

    return game_ids


if __name__ == "__main__":
    print("[DEBUG] Script started")
    ids = fetch_game_ids(debug=True)
    print("[DEBUG] Script finished")
    print("Game IDs:", ids)
