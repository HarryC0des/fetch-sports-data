import time
from typing import List

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


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def extract_recap_text(html) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    recap_container = (
        soup.select_one("div.Story__Body")
        or soup.select_one("div.Story__Body.t__body")
        or soup.select_one("article")
    )
    paragraphs = recap_container.find_all("p") if recap_container else soup.find_all("p")
    return [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]


def fetch_recap(url):
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
    input_path = get_env("GAME_IDS_PATH", default="/tmp/game_ids.json")
    output_path = get_env("OUTPUT_PATH", default="/tmp/recaps.json")
    delay_seconds = float(get_env("ESPN_REQUEST_DELAY_SECONDS", default="1"))
    failure_threshold = float(get_env("FAILURE_ALERT_THRESHOLD", default="0.5"))

    log_start("fetch_game_recaps", run_id, run_date)

    game_payload = load_json(input_path)
    games = game_payload.get("games", [])
    log_info(f"Loaded {len(games)} games from {input_path}")

    recap_games = []
    errors = []

    for game in games:
        game_id = game.get("game_id")
        recap_url = game.get("recap_url")
        if not game_id or not recap_url:
            errors.append({"game_id": game_id, "error": "missing_game_id_or_url"})
            continue

        try:
            response = fetch_recap(recap_url)
        except Exception as exc:
            log_error(f"Request failed for game_id={game_id}: {exc}")
            errors.append({"game_id": game_id, "error": "request_failed"})
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            continue

        if response.status_code == 403:
            log_warning(f"Blocked by ESPN for game_id={game_id}")
            errors.append({"game_id": game_id, "error": "blocked"})
        elif response.status_code == 404:
            log_warning(f"Recap missing for game_id={game_id}")
            errors.append({"game_id": game_id, "error": "not_found"})
        elif response.status_code != 200:
            log_error(f"Non-200 response for game_id={game_id}: {response.status_code}")
            errors.append(
                {"game_id": game_id, "error": f"http_{response.status_code}"}
            )
        else:
            recap_text = extract_recap_text(response.text)
            if not recap_text:
                log_warning(f"No recap text found for game_id={game_id}")
                errors.append({"game_id": game_id, "error": "no_recap_text"})
            else:
                recap_games.append(
                    {
                        "game_id": game_id,
                        "game_date": game.get("game_date"),
                        "teams": game.get("teams", []),
                        "team_aliases": game.get("team_aliases", []),
                        "recap_text": recap_text,
                        "source_url": recap_url,
                    }
                )

        if delay_seconds > 0:
            time.sleep(delay_seconds)

    if games:
        failure_rate = len(errors) / len(games)
        if failure_rate >= failure_threshold:
            print(
                f"::warning::High failure rate while fetching recaps: {failure_rate:.2%}"
            )

    output_payload = {
        "run_id": run_id,
        "run_date": run_date,
        "schema_version": "v1",
        "source": "espn_recaps",
        "games": recap_games,
        "errors": errors,
    }
    write_json(output_path, output_payload)

    log_end(
        "fetch_game_recaps",
        f"recaps={len(recap_games)} errors={len(errors)} output={output_path}",
    )


if __name__ == "__main__":
    main()
