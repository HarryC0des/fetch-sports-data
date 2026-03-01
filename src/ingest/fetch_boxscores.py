import time
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from src.pipeline.common import (
    build_run_id,
    get_env,
    load_json,
    log_end,
    log_error,
    log_info,
    log_start,
    log_warning,
    resolve_run_date,
    write_json,
)
from src.pipeline.http_utils import request_with_retry


BOX_SCORE_URL = "https://www.espn.com/nba/boxscore/_/gameId/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def fetch_boxscore(url):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = request_with_retry(
        "GET",
        url,
        headers=headers,
        timeout=15,
        max_retries=3,
        retry_statuses={429, 500, 502, 503, 504},
        backoff_type="exponential",
        base_delay=2,
        max_delay=10,
        jitter_max=1,
    )
    return response


def main():
    run_id = build_run_id()
    run_date = resolve_run_date()
    input_path = get_env("GAME_IDS_PATH", default="artifacts/game_ids.json")
    output_path = get_env("OUTPUT_PATH", default="artifacts/boxscores.json")
    delay_seconds = float(get_env("ESPN_REQUEST_DELAY_SECONDS", default="1"))

    log_start("fetch_boxscores", run_id, run_date)

    game_payload = load_json(input_path)
    games = game_payload.get("games", [])
    log_info(f"Loaded {len(games)} games from {input_path}")

    results = {}

    for game in games:
        game_id = game.get("game_id")
        if not game_id:
            log_warning("Skipping game without game_id")
            continue

        url = f"{BOX_SCORE_URL}{game_id}"
        try:
            response = fetch_boxscore(url)
        except Exception as exc:
            log_error(f"Boxscore request failed for game_id={game_id}: {exc}")
            results[game_id] = {"url": url, "error": "request_failed"}
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            continue

        if response.status_code != 200:
            log_error(
                f"Boxscore response error for game_id={game_id}: {response.status_code}"
            )
            results[game_id] = {"url": url, "error": f"http_{response.status_code}"}
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("div.Card.Card__TableTopBorder")
        if not cards:
            log_warning(f"Card__TableTopBorder not found for game_id={game_id}")
            results[game_id] = {
                "url": url,
                "error": "Card__TableTopBorder not found",
            }
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            continue

        html_blocks = [str(card) for card in cards]
        text_blocks = [
            card.get_text(separator=" ", strip=True) for card in cards
        ]
        results[game_id] = {
            "url": url,
            "html": "\n".join(html_blocks),
            "text": " ".join(text_blocks),
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

        if delay_seconds > 0:
            time.sleep(delay_seconds)

    write_json(output_path, results)
    log_end(
        "fetch_boxscores",
        f"boxscores={len(results)} output={output_path}",
    )


if __name__ == "__main__":
    main()
