import datetime
from collections import Counter
import requests

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
from src.pipeline.style_utils import normalize_style, style_label
from src.pipeline.team_utils import matches_team


def fetch_supabase_rows(base_url, api_key, table, query):
    url = f"{base_url}/rest/v1/{table}?{query}"
    headers = {"apikey": api_key, "Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers, timeout=20)
    except requests.RequestException as exc:
        log_error(f"Supabase request failed: {exc}")
        return []

    if response.status_code != 200:
        log_error(f"Supabase error {response.status_code} for {table}")
        return []

    return response.json()


def parse_run_date(value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return datetime.date.today()


def parse_game_date(value):
    if not value:
        return None
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def should_send_user(user_frequency, run_date, weekly_send_day):
    frequency = (user_frequency or "daily").strip().lower()
    if frequency != "weekly":
        return True
    day_name = run_date.strftime("%A").lower()
    return day_name == weekly_send_day


def main():
    run_id = build_run_id()
    run_date = resolve_run_date()
    input_path = get_env("TAKES_PATH", default="/tmp/takes.json")
    output_path = get_env("OUTPUT_PATH", default="/tmp/deliveries.json")

    supabase_url = get_env("SUPABASE_URL", required=True)
    supabase_key = get_env("SUPABASE_KEY", required=True)
    users_table = get_env("SUPABASE_USERS_TABLE", default="users")
    interests_table = get_env("SUPABASE_INTERESTS_TABLE", default="interests")
    users_query = get_env(
        "SUPABASE_USERS_QUERY",
        default="select=id,email,frequency,take_style",
    )
    interests_query = get_env(
        "SUPABASE_INTERESTS_QUERY",
        default="select=user_id,team",
    )

    max_takes = int(get_env("MAX_TAKES_PER_EMAIL", default="3"))
    weekly_send_day = get_env("WEEKLY_SEND_DAY", default="monday").strip().lower()

    log_start("personalize", run_id, run_date)

    takes_payload = load_json(input_path)
    takes = takes_payload.get("takes", [])
    log_info(f"Loaded {len(takes)} takes from {input_path}")
    style_counts = Counter(
        normalize_style(take.get("style") or "mix") for take in takes
    )
    available_teams = sorted(
        {team for take in takes for team in (take.get("teams") or [])}
    )
    log_info(f"Available take styles: {dict(style_counts)}")
    if available_teams:
        log_info(f"Available teams in takes: {', '.join(available_teams)}")
    else:
        log_info("No teams found in takes payload")

    users = fetch_supabase_rows(supabase_url, supabase_key, users_table, users_query)
    interests = fetch_supabase_rows(
        supabase_url, supabase_key, interests_table, interests_query
    )

    log_info(f"Loaded {len(users)} users and {len(interests)} interests")

    user_teams = {}
    for interest in interests:
        user_id = interest.get("user_id")
        team = interest.get("team")
        if not user_id or not team:
            continue
        user_teams.setdefault(str(user_id), []).append(team)

    deliveries = []
    run_date_obj = parse_run_date(run_date)

    for user in users:
        user_id = str(user.get("id"))
        email = user.get("email")
        if not user_id or not email:
            log_warning("Skipping user with missing id or email")
            continue

        frequency = (user.get("frequency") or "daily").strip().lower()
        if not should_send_user(frequency, run_date_obj, weekly_send_day):
            continue

        teams = user_teams.get(user_id, [])
        if not teams:
            log_info(f"Skipping user_id={user_id} with no teams selected")
            continue

        desired_style = normalize_style(user.get("take_style") or "mix")
        matching = []
        for take in takes:
            take_style = normalize_style(take.get("style") or "mix")
            if take_style != desired_style:
                continue
            aliases = take.get("team_aliases") or take.get("teams") or []
            matched_any = False
            for team in teams:
                if matches_team(team, aliases):
                    matched_any = True
            if matched_any:
                matching.append(take)

        if not matching:
            log_info(
                f"Skipping user_id={user_id} no matching takes "
                f"(style={desired_style} teams={', '.join(teams)})"
            )
            continue

        matching.sort(
            key=lambda take: parse_game_date(take.get("game_date"))
            or datetime.datetime.min,
            reverse=True,
        )
        selected = matching[:max_takes]

        subject = f"{frequency.title()} NBA Takes - {run_date}"
        unsubscribe_url = user.get("unsubscribe_url")

        deliveries.append(
            {
                "user_id": user_id,
                "email": email,
                "frequency": frequency,
                "take_style": style_label(desired_style),
                "teams": teams,
                "subject": subject,
                "takes": selected,
                "unsubscribe_url": unsubscribe_url,
            }
        )

    output_payload = {
        "run_id": run_id,
        "run_date": run_date,
        "schema_version": "v1",
        "source": "personalization",
        "deliveries": deliveries,
    }
    write_json(output_path, output_payload)

    log_end(
        "personalize",
        f"deliveries={len(deliveries)} output={output_path}",
    )


if __name__ == "__main__":
    main()
