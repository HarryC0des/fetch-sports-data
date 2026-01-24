import os

from src.pipeline.common import (
    build_run_id,
    get_env,
    log_end,
    log_error,
    log_info,
    log_start,
    log_warning,
    resolve_run_date,
    write_json,
)
from src.pipeline.http_utils import request_with_retry
from src.pipeline.team_utils import build_game_aliases


SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
RECAP_BASE_URL = "https://www.espn.com/nba/recap/_/gameId/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def resolve_scoreboard_date():
    scoreboard_date = get_env("ESPN_SCOREBOARD_DATE", default=None)
    if not scoreboard_date:
        scoreboard_date = get_env("SCOREBOARD_DATE", default=None)
    if scoreboard_date:
        cleaned = scoreboard_date.replace("-", "")
        if len(cleaned) != 8 or not cleaned.isdigit():
            raise ValueError("Invalid SCOREBOARD_DATE. Use YYYY-MM-DD or YYYYMMDD.")
        return cleaned
    return resolve_run_date().replace("-", "")


def extract_team_info(competitor):
    team = competitor.get("team", {}) if competitor else {}
    return {
        "name": team.get("displayName"),
        "short_name": team.get("shortDisplayName"),
        "abbreviation": team.get("abbreviation"),
        "home_away": competitor.get("homeAway") if competitor else None,
    }


def fetch_scoreboard(scoreboard_date):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = request_with_retry(
        "GET",
        SCOREBOARD_URL,
        headers=headers,
        params={"dates": scoreboard_date},
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
    output_path = get_env("OUTPUT_PATH", default="/tmp/game_ids.json")
    scoreboard_date = resolve_scoreboard_date()

    log_start("fetch_game_ids", run_id, run_date)
    log_info(f"Scoreboard date: {scoreboard_date}")

    games = []
    errors = []

    try:
        response = fetch_scoreboard(scoreboard_date)
    except Exception as exc:
        log_error(f"Scoreboard request failed: {exc}")
        errors.append({"type": "request_error", "detail": str(exc)})
        response = None

    if response is None:
        log_warning("No response received; writing empty game list.")
    elif response.status_code != 200:
        log_error(f"Non-200 response: {response.status_code}")
        errors.append({"type": "http_error", "status": response.status_code})
    else:
        payload = response.json()
        events = payload.get("events") or []
        log_info(f"Found {len(events)} events")

        for event in events:
            game_id = event.get("id")
            competitions = event.get("competitions") or []
            competition = competitions[0] if competitions else {}
            competitors = competition.get("competitors") or []

            home_team = None
            away_team = None
            for competitor in competitors:
                team_info = extract_team_info(competitor)
                if competitor.get("homeAway") == "home":
                    home_team = team_info
                elif competitor.get("homeAway") == "away":
                    away_team = team_info

            home_team = home_team or {}
            away_team = away_team or {}
            team_aliases = build_game_aliases(home_team, away_team)

            teams = [home_team.get("name"), away_team.get("name")]
            teams = [team for team in teams if team]

            if not game_id:
                errors.append({"type": "missing_game_id", "detail": event.get("name")})
                continue

            games.append(
                {
                    "game_id": str(game_id),
                    "game_date": event.get("date"),
                    "home_team": home_team,
                    "away_team": away_team,
                    "teams": teams,
                    "team_aliases": team_aliases,
                    "recap_url": f"{RECAP_BASE_URL}{game_id}",
                }
            )

    output_payload = {
        "run_id": run_id,
        "run_date": run_date,
        "schema_version": "v1",
        "source": "espn_scoreboard",
        "scoreboard_date": scoreboard_date,
        "games": games,
        "errors": errors,
    }
    write_json(output_path, output_payload)

    log_end(
        "fetch_game_ids",
        f"games={len(games)} errors={len(errors)} output={output_path}",
    )


if __name__ == "__main__":
    main()
