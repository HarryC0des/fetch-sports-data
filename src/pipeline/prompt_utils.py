import json
from pathlib import Path

from .common import get_env


def _repo_root():
    return Path(__file__).resolve().parents[2]


def load_prompt_version():
    version_override = get_env("PROMPT_VERSION", default=None)
    versions_path = _repo_root() / "prompts" / "versions.json"
    if not versions_path.exists():
        raise FileNotFoundError(f"Missing prompt versions file: {versions_path}")

    versions = json.loads(versions_path.read_text(encoding="utf-8"))
    if version_override:
        return version_override
    active = versions.get("active_version")
    if not active:
        raise RuntimeError("No active prompt version configured.")
    return active


def load_prompt_assets(version):
    base_dir = _repo_root() / "prompts" / version
    base_system_path = base_dir / "base_system.txt"
    output_rules_path = base_dir / "output_rules.txt"
    styles_path = base_dir / "styles.json"

    if not base_system_path.exists():
        raise FileNotFoundError(f"Missing base system prompt: {base_system_path}")
    if not output_rules_path.exists():
        raise FileNotFoundError(f"Missing output rules prompt: {output_rules_path}")
    if not styles_path.exists():
        raise FileNotFoundError(f"Missing styles prompt: {styles_path}")

    base_system = base_system_path.read_text(encoding="utf-8").strip()
    output_rules = output_rules_path.read_text(encoding="utf-8").strip()
    styles = json.loads(styles_path.read_text(encoding="utf-8"))
    return base_system, output_rules, styles


def build_system_prompt(base_system, output_rules):
    return f"{base_system}\n\n{output_rules}".strip()


def build_user_prompt(
    *,
    teams,
    facts,
    style,
    style_guidance,
    max_words,
    audience,
    disclaimer,
    focus_team=None,
):
    team_line = ", ".join(teams) if teams else "Unknown teams"
    fact_lines = "\n".join(f"- {fact}" for fact in facts)
    prompt = (
        "Facts:\n"
        f"- Teams: {team_line}\n"
        f"{fact_lines}\n\n"
        "Instructions:\n"
        "- League: NBA\n"
        f"- Style: {style}\n"
        f"- Max length: {max_words} words\n"
        f"- Audience: {audience}\n"
        f"- Tone guidance: {style_guidance}\n"
        f"- Factual source disclaimer: {disclaimer}\n"
        "- If facts are insufficient, respond with: INSUFFICIENT FACTS TO GENERATE TAKE\n"
    )
    if focus_team:
        prompt = f"{prompt}\nEnsure takes focus on {focus_team}"
    return prompt
