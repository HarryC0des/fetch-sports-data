"""
Flask Web Application for Sports Takes Newsletter signup and analysis.
"""
from datetime import datetime, timezone
import os
import re
from urllib.parse import quote

import requests
from flask import Flask, render_template, jsonify, request

from src.analyzer import analyze_records_by_date

app = Flask(__name__, template_folder="templates")


TEAM_OPTIONS = [
    "Atlanta Hawks",
    "Boston Celtics",
    "Brooklyn Nets",
    "Charlotte Hornets",
    "Chicago Bulls",
    "Cleveland Cavaliers",
    "Dallas Mavericks",
    "Denver Nuggets",
    "Detroit Pistons",
    "Golden State Warriors",
    "Houston Rockets",
    "Indiana Pacers",
    "LA Clippers",
    "Los Angeles Lakers",
    "Memphis Grizzlies",
    "Miami Heat",
    "Milwaukee Bucks",
    "Minnesota Timberwolves",
    "New Orleans Pelicans",
    "New York Knicks",
    "Oklahoma City Thunder",
    "Orlando Magic",
    "Philadelphia 76ers",
    "Phoenix Suns",
    "Portland Trail Blazers",
    "Sacramento Kings",
    "San Antonio Spurs",
    "Toronto Raptors",
    "Utah Jazz",
    "Washington Wizards",
]

TAKE_STYLES = [
    {"value": "factual", "label": "Factual"},
    {"value": "hot_takes", "label": "Hot Takes"},
    {"value": "analytical", "label": "Analytical"},
    {"value": "nuanced", "label": "Nuanced"},
    {"value": "mix", "label": "Mix"},
]

EMAIL_FREQUENCIES = ["daily", "weekly"]
MAX_TEAMS = 5
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def supabase_headers(api_key, schema="public", include_json=True):
    headers = {"apikey": api_key, "Authorization": f"Bearer {api_key}"}
    if schema:
        headers["Accept-Profile"] = schema
        if include_json:
            headers["Content-Profile"] = schema
    if include_json:
        headers["Content-Type"] = "application/json"
        headers["Prefer"] = "return=representation"
    return headers


def validate_signup_payload(payload):
    errors = {}

    name = str(payload.get("name", "")).strip()
    if not name:
        errors["name"] = "Name is required."

    email = str(payload.get("email", "")).strip().lower()
    if not email or not EMAIL_REGEX.match(email):
        errors["email"] = "Enter a valid email address."

    teams = payload.get("teams", [])
    if not isinstance(teams, list):
        errors["teams"] = "Select up to five teams."
        teams = []
    teams = [str(team).strip() for team in teams if str(team).strip()]
    invalid_teams = [team for team in teams if team not in TEAM_OPTIONS]
    if invalid_teams:
        errors["teams"] = "One or more selected teams are invalid."
    if len(set(teams)) != len(teams):
        errors["teams"] = "Duplicate teams selected."
    if len(teams) == 0:
        errors["teams"] = "Select at least one team."
    if len(teams) > MAX_TEAMS:
        errors["teams"] = "You can select up to five teams."

    style = str(payload.get("style", "")).strip().lower()
    allowed_styles = {item["value"] for item in TAKE_STYLES}
    if style not in allowed_styles:
        errors["style"] = "Select a valid take style."

    frequency = str(payload.get("frequency", "")).strip().lower()
    if frequency not in EMAIL_FREQUENCIES:
        errors["frequency"] = "Select a valid frequency."

    return errors, {
        "name": name,
        "email": email,
        "teams": teams,
        "style": style,
        "frequency": frequency,
    }


def normalize_base_url(base_url):
    return base_url.rstrip("/")


def encode_table_name(table_name):
    if not table_name:
        return table_name
    if re.match(r"^[a-z_][a-z0-9_]*$", table_name):
        return table_name
    if table_name.startswith('"') and table_name.endswith('"'):
        quoted = table_name
    else:
        quoted = f'"{table_name}"'
    return quote(quoted, safe="")


def build_table_paths(table_name):
    raw = quote(table_name, safe="")
    quoted = encode_table_name(table_name)
    if quoted == raw:
        return [raw]
    return [quoted, raw]


def is_missing_table(response):
    if response.status_code != 404:
        return False
    try:
        payload = response.json()
    except ValueError:
        return False
    return payload.get("code") == "PGRST205"


def fetch_user_by_email(base_url, api_key, schema, table, email):
    last_response = None
    for table_path in build_table_paths(table):
        url = f"{base_url}/rest/v1/{table_path}?select=id,email&email=eq.{email}"
        response = requests.get(
            url,
            headers=supabase_headers(api_key, schema=schema, include_json=False),
            timeout=20,
        )
        last_response = response
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        if is_missing_table(response):
            continue
        raise RuntimeError(
            f"Supabase user lookup failed: {response.status_code} {response.text}"
        )

    raise RuntimeError(
        f"Supabase user lookup failed: {last_response.status_code} {last_response.text}"
    )


def create_user(base_url, api_key, schema, table, payload):
    last_response = None
    for table_path in build_table_paths(table):
        url = f"{base_url}/rest/v1/{table_path}"
        response = requests.post(
            url,
            headers=supabase_headers(api_key, schema=schema),
            json=payload,
            timeout=20,
        )
        last_response = response
        if response.status_code in (200, 201):
            data = response.json()
            if not data:
                raise RuntimeError("Supabase user create did not return data.")
            return data[0]["id"]
        if is_missing_table(response):
            continue
        raise RuntimeError(
            f"Supabase user create failed: {response.status_code} {response.text}"
        )

    raise RuntimeError(
        f"Supabase user create failed: {last_response.status_code} {last_response.text}"
    )


def update_user(base_url, api_key, schema, table, user_id, payload):
    last_response = None
    for table_path in build_table_paths(table):
        url = f"{base_url}/rest/v1/{table_path}?id=eq.{user_id}"
        response = requests.patch(
            url,
            headers=supabase_headers(api_key, schema=schema),
            json=payload,
            timeout=20,
        )
        last_response = response
        if response.status_code in (200, 204):
            return
        if is_missing_table(response):
            continue
        raise RuntimeError(
            f"Supabase user update failed: {response.status_code} {response.text}"
        )

    raise RuntimeError(
        f"Supabase user update failed: {last_response.status_code} {last_response.text}"
    )


def replace_interests(base_url, api_key, schema, table, user_id, teams):
    headers = supabase_headers(api_key, schema=schema)
    last_response = None
    for table_path in build_table_paths(table):
        delete_url = f"{base_url}/rest/v1/{table_path}?user_id=eq.{user_id}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=20)
        last_response = delete_response
        if is_missing_table(delete_response):
            continue
        if delete_response.status_code not in (200, 204):
            raise RuntimeError(
                f"Failed to clear existing interests: {delete_response.status_code} "
                f"{delete_response.text}"
            )

        payload = [{"user_id": user_id, "team": team} for team in teams]
        insert_url = f"{base_url}/rest/v1/{table_path}"
        insert_response = requests.post(
            insert_url, headers=headers, json=payload, timeout=20
        )
        if insert_response.status_code not in (200, 201):
            raise RuntimeError(
                f"Failed to insert interests: {insert_response.status_code} "
                f"{insert_response.text}"
            )
        return

    raise RuntimeError(
        f"Failed to clear existing interests: {last_response.status_code} "
        f"{last_response.text}"
    )


@app.route("/")
def signup_page():
    return render_template(
        "index.html",
        teams=TEAM_OPTIONS,
        styles=TAKE_STYLES,
        frequencies=EMAIL_FREQUENCIES,
        max_teams=MAX_TEAMS,
    )


@app.route("/analysis")
def analysis_page():
    return render_template("analysis.html")


@app.route("/api/signup", methods=["POST"])
def api_signup():
    payload = request.get_json(silent=True) or {}
    errors, cleaned = validate_signup_payload(payload)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase_schema = os.getenv("SUPABASE_SCHEMA", "public")
    users_table = os.getenv("SUPABASE_USERS_TABLE", "users")
    interests_table = os.getenv("SUPABASE_INTERESTS_TABLE", "interests")
    if not supabase_url or not supabase_key:
        return jsonify({"success": False, "error": "Server misconfigured."}), 500

    supabase_url = normalize_base_url(supabase_url)
    timestamp = now_iso()
    user_payload = {
        "name": cleaned["name"],
        "email": cleaned["email"],
        "take_style": cleaned["style"],
        "frequency": cleaned["frequency"],
        "updated_at": timestamp,
    }

    try:
        existing_user = fetch_user_by_email(
            supabase_url, supabase_key, supabase_schema, users_table, cleaned["email"]
        )
        if existing_user:
            update_user(
                supabase_url,
                supabase_key,
                supabase_schema,
                users_table,
                existing_user["id"],
                user_payload,
            )
            user_id = existing_user["id"]
        else:
            user_payload["created_at"] = timestamp
            user_id = create_user(
                supabase_url,
                supabase_key,
                supabase_schema,
                users_table,
                user_payload,
            )

        replace_interests(
            supabase_url,
            supabase_key,
            supabase_schema,
            interests_table,
            user_id,
            cleaned["teams"],
        )
    except Exception as exc:
        print(f"[ERROR] Signup failed: {exc}")
        return jsonify({"success": False, "error": "Signup failed."}), 500

    return jsonify({"success": True, "message": "Signup saved."})


@app.route("/api/analyze", methods=["GET"])
def api_analyze():
    try:
        print("[DEBUG] API /analyze called")
        results = analyze_records_by_date()
        print(f"[DEBUG] Analysis returned results for {len(results)} dates")
        return jsonify({"success": True, "data": results})
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("[INFO] Starting Sports Takes Web App")
    print("[INFO] Visit http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
