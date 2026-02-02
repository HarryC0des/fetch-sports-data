import time
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
from src.pipeline.http_utils import request_with_retry
from src.pipeline.prompt_utils import (
    build_system_prompt,
    build_user_prompt,
    load_prompt_assets,
    load_prompt_version,
)
from src.pipeline.style_utils import normalize_style, style_label
from src.pipeline.team_utils import matches_team


API_URL_DEFAULT = "https://openrouter.ai/api/v1/chat/completions"
MODEL_DEFAULT = "tngtech/tng-r1t-chimera:free"

STYLE_KEYS = ["factual", "hot_takes", "analytical", "nuanced", "mix"]


def call_llm(
    api_url,
    api_key,
    model,
    messages,
    temperature,
    max_tokens,
    referer,
    title,
):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    response = request_with_retry(
        "POST",
        api_url,
        headers=headers,
        json=payload,
        timeout=30,
        max_retries=2,
        retry_statuses={429},
        backoff_type="fixed",
        base_delay=5,
    )
    return response


def fetch_supabase_rows(base_url, api_key, table, query):
    url = f"{base_url}/rest/v1/{table}?{query}"
    headers = {"apikey": api_key, "Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code != 200:
        raise RuntimeError(
            f"Supabase request failed: {response.status_code} {response.text}"
        )
    return response.json()


def main():
    run_id = build_run_id()
    run_date = resolve_run_date()
    input_path = get_env("FACTS_PATH", default="/tmp/facts.json")
    output_path = get_env("OUTPUT_PATH", default="/tmp/takes.json")
    api_url = get_env("OPEN_ROUTER_API_URL", default=API_URL_DEFAULT)
    model = get_env("OPEN_ROUTER_MODEL", default=MODEL_DEFAULT)
    api_key = get_env("OPEN_ROUTER_KEY", required=True)
    referer = get_env(
        "OPEN_ROUTER_REFERER",
        default="https://github.com/HarryC0des/fetch-sports-data",
    )
    title = get_env("OPEN_ROUTER_TITLE", default="Sports Takes Newsletter")
    supabase_url = get_env("SUPABASE_URL", required=True).rstrip("/")
    supabase_key = get_env("SUPABASE_KEY", required=True)
    users_table = get_env("SUPABASE_USERS_TABLE", default="users")
    interests_table = get_env("SUPABASE_INTERESTS_TABLE", default="interests")
    users_query = get_env("SUPABASE_USERS_QUERY", default="select=id,take_style")
    interests_query = get_env(
        "SUPABASE_INTERESTS_QUERY", default="select=user_id,team"
    )
    max_words = int(get_env("MAX_TAKE_WORDS", default="120"))
    max_tokens = int(get_env("MAX_TAKE_TOKENS", default="220"))
    temperature = float(get_env("TAKE_TEMPERATURE", default="0.6"))
    audience = get_env("TAKE_AUDIENCE", default="Casual NBA fans")
    disclaimer = get_env("TAKE_DISCLAIMER", default="Based on ESPN recap text.")
    failure_threshold = float(get_env("FAILURE_ALERT_THRESHOLD", default="0.5"))
    pause_seconds = float(get_env("LLM_REQUEST_DELAY_SECONDS", default="0"))

    log_start("generate_takes", run_id, run_date)

    prompt_version = load_prompt_version()
    base_system, output_rules, styles = load_prompt_assets(prompt_version)
    system_prompt = build_system_prompt(base_system, output_rules)

    facts_payload = load_json(input_path)
    games = facts_payload.get("games", [])
    log_info(f"Loaded {len(games)} fact groups from {input_path}")

    users = fetch_supabase_rows(
        supabase_url, supabase_key, users_table, users_query
    )
    interests = fetch_supabase_rows(
        supabase_url, supabase_key, interests_table, interests_query
    )
    log_info(f"Loaded {len(users)} users and {len(interests)} interests")

    user_styles = {}
    for user in users:
        user_id = user.get("id")
        if user_id is None:
            continue
        style_key = normalize_style(user.get("take_style") or "mix")
        if style_key not in STYLE_KEYS:
            continue
        user_styles[str(user_id)] = style_key

    team_style_map = {}
    for interest in interests:
        user_id = interest.get("user_id")
        team = interest.get("team")
        if user_id is None or not team:
            continue
        style_key = user_styles.get(str(user_id))
        if not style_key:
            continue
        team_style_map.setdefault(team, set()).add(style_key)

    if not team_style_map:
        log_warning("No team/style preferences found; skipping take generation.")
        output_payload = {
            "run_id": run_id,
            "run_date": run_date,
            "schema_version": "v1",
            "source": "openrouter",
            "prompt_version": prompt_version,
            "model": model,
            "takes": [],
            "errors": [],
        }
        write_json(output_path, output_payload)
        log_end("generate_takes", "takes=0 errors=0 output=%s" % output_path)
        return

    style_counts = Counter(user_styles.values())
    log_info(f"User take style counts: {dict(style_counts)}")
    log_info(f"Unique teams requested: {len(team_style_map)}")

    takes = []
    errors = []
    total_requests = 0
    failed_requests = 0
    considered_games = 0
    skipped_games = 0

    for game in games:
        facts = game.get("facts") or []
        if not facts:
            errors.append({"game_id": game.get("game_id"), "error": "missing_facts"})
            continue

        game_aliases = game.get("team_aliases") or game.get("teams") or []
        required_styles = set()
        for team_name, team_styles in team_style_map.items():
            if matches_team(team_name, game_aliases):
                required_styles.update(team_styles)

        if not required_styles:
            skipped_games += 1
            continue

        considered_games += 1

        for style_key in STYLE_KEYS:
            if style_key not in required_styles:
                continue
            style_text = styles.get(style_key)
            if not style_text:
                log_warning(f"Missing style prompt for {style_key}")
                continue

            user_prompt = build_user_prompt(
                teams=game.get("teams", []),
                facts=facts,
                style=style_label(style_key),
                style_guidance=style_text,
                max_words=max_words,
                audience=audience,
                disclaimer=disclaimer,
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            total_requests += 1
            response = call_llm(
                api_url=api_url,
                api_key=api_key,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                referer=referer,
                title=title,
            )

            if response.status_code != 200:
                failed_requests += 1
                response_detail = response.text.strip().replace("\n", " ")
                if len(response_detail) > 300:
                    response_detail = response_detail[:300] + "..."
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    log_warning(
                        f"LLM Retry-After for game_id={game.get('game_id')}: {retry_after}"
                    )
                log_error(
                    f"LLM error for game_id={game.get('game_id')} style={style_key}: "
                    f"{response.status_code} {response_detail}"
                )
                errors.append(
                    {
                        "game_id": game.get("game_id"),
                        "style": style_key,
                        "error": f"http_{response.status_code}",
                    }
                )
                if pause_seconds > 0:
                    time.sleep(pause_seconds)
                continue

            data = response.json()
            if "error" in data:
                failed_requests += 1
                error_message = data.get("error", {}).get("message", "unknown_error")
                log_error(f"LLM response error: {error_message}")
                errors.append(
                    {
                        "game_id": game.get("game_id"),
                        "style": style_key,
                        "error": error_message,
                    }
                )
                if pause_seconds > 0:
                    time.sleep(pause_seconds)
                continue

            choices = data.get("choices") or []
            if not choices:
                failed_requests += 1
                log_error(
                    f"No LLM choices for game_id={game.get('game_id')} style={style_key}"
                )
                errors.append(
                    {
                        "game_id": game.get("game_id"),
                        "style": style_key,
                        "error": "no_choices",
                    }
                )
                if pause_seconds > 0:
                    time.sleep(pause_seconds)
                continue

            content = choices[0].get("message", {}).get("content", "").strip()
            normalized = content.upper()
            if not content or normalized.startswith("INSUFFICIENT FACTS"):
                errors.append(
                    {
                        "game_id": game.get("game_id"),
                        "style": style_key,
                        "error": "insufficient_facts",
                    }
                )
                if pause_seconds > 0:
                    time.sleep(pause_seconds)
                continue

            takes.append(
                {
                    "game_id": game.get("game_id"),
                    "game_date": game.get("game_date"),
                    "teams": game.get("teams", []),
                    "team_aliases": game.get("team_aliases", []),
                    "style": normalize_style(style_key),
                    "take_text": content,
                }
            )

            if pause_seconds > 0:
                time.sleep(pause_seconds)

    if total_requests:
        failure_rate = failed_requests / total_requests
        if failure_rate >= failure_threshold:
            print(f"::warning::High LLM failure rate: {failure_rate:.2%}")
    log_info(
        f"Games considered={considered_games} skipped={skipped_games} total={len(games)}"
    )

    output_payload = {
        "run_id": run_id,
        "run_date": run_date,
        "schema_version": "v1",
        "source": "openrouter",
        "prompt_version": prompt_version,
        "model": model,
        "takes": takes,
        "errors": errors,
    }
    write_json(output_path, output_payload)

    log_end(
        "generate_takes",
        f"takes={len(takes)} errors={len(errors)} output={output_path}",
    )


if __name__ == "__main__":
    main()
