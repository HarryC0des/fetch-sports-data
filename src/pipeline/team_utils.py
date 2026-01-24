import re


def normalize_team(value):
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]", "", value.lower())


def build_team_aliases(team):
    aliases = []
    for key in ("name", "short_name", "abbreviation"):
        value = team.get(key)
        if value:
            aliases.append(value)
    return dedupe_aliases(aliases)


def dedupe_aliases(aliases):
    seen = set()
    cleaned = []
    for alias in aliases:
        normalized = normalize_team(alias)
        if normalized and normalized not in seen:
            cleaned.append(alias)
            seen.add(normalized)
    return cleaned


def build_game_aliases(home_team, away_team):
    aliases = build_team_aliases(home_team) + build_team_aliases(away_team)
    return dedupe_aliases(aliases)


def matches_team(user_team, team_aliases):
    user_norm = normalize_team(user_team)
    if not user_norm:
        return False
    for alias in team_aliases:
        alias_norm = normalize_team(alias)
        if not alias_norm:
            continue
        if user_norm == alias_norm:
            return True
        if len(user_norm) >= 4 and user_norm in alias_norm:
            return True
    return False
