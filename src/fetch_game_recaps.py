def fetch_recap_text(game_id, debug=True):
    url = f"{BASE_URL}{game_id}"

    if debug:
        print(f"[DEBUG] Fetching recap for gameId={game_id}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    recap_div = (
    soup.select_one("div.Story__Body.t__body") or
    soup.select_one("div[class*='Story__Body']")
    )

    if not recap_div:
        print(f"[WARNING] No recap body found for gameId={game_id}")
        return None

    paragraphs = recap_div.find_all("p")

    text_blocks = [
        p.get_text(strip=True)
        for p in paragraphs
        if p.get_text(strip=True)
    ]

    if debug:
        print(f"[DEBUG] Extracted {len(text_blocks)} paragraphs for gameId={game_id}")

    return text_blocks
