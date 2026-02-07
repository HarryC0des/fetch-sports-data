import re

from src.pipeline.common import (
    build_run_id,
    get_env,
    load_json,
    log_end,
    log_info,
    log_start,
    log_warning,
    resolve_run_date,
    write_json,
)


def split_sentences(text):
    return [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]


def sentence_mentions_team(sentence, alias_values):
    sentence_lower = sentence.lower()
    for alias in alias_values:
        if not alias:
            continue
        if len(alias) <= 3:
            if re.search(rf"\b{re.escape(alias)}\b", sentence_lower):
                return True
        elif alias in sentence_lower:
            return True
    return False


def select_fact_sentences(paragraphs, team_aliases, max_sentences, max_length):
    sentences = []
    for paragraph in paragraphs:
        sentences.extend(split_sentences(paragraph))

    if not sentences:
        return []

    alias_values = [alias.lower() for alias in team_aliases if alias]

    matched = [s for s in sentences if sentence_mentions_team(s, alias_values)]
    if not matched:
        matched = sentences

    deduped = []
    seen = set()
    for sentence in matched:
        normalized = sentence.lower().strip()
        if normalized not in seen:
            deduped.append(sentence[:max_length])
            seen.add(normalized)
        if len(deduped) >= max_sentences:
            break
    return deduped


def main():
    run_id = build_run_id()
    run_date = resolve_run_date()
    input_path = get_env("RECAPS_PATH", default="/tmp/recaps.json")
    output_path = get_env("OUTPUT_PATH", default="/tmp/facts.json")
    max_sentences = int(get_env("MAX_FACT_SENTENCES", default="3"))
    max_length = int(get_env("MAX_FACT_LENGTH", default="300"))

    log_start("extract_facts", run_id, run_date)

    recaps_payload = load_json(input_path)
    games = recaps_payload.get("games", [])
    log_info(f"Loaded {len(games)} recaps from {input_path}")

    fact_games = []
    errors = []

    for recap in games:
        recap_text = recap.get("recap_text") or []
        if not recap_text:
            errors.append({"game_id": recap.get("game_id"), "error": "missing_recap"})
            continue

        facts = select_fact_sentences(
            recap_text,
            recap.get("team_aliases", []),
            max_sentences,
            max_length,
        )
        if not facts:
            log_warning(f"No facts extracted for game_id={recap.get('game_id')}")
            errors.append({"game_id": recap.get("game_id"), "error": "no_facts"})
            continue

        fact_games.append(
            {
                "game_id": recap.get("game_id"),
                "game_date": recap.get("game_date"),
                "teams": recap.get("teams", []),
                "team_aliases": recap.get("team_aliases", []),
                "facts": facts,
                "source_url": recap.get("source_url"),
            }
        )

    output_payload = {
        "run_id": run_id,
        "run_date": run_date,
        "schema_version": "v1",
        "source": "recap_fact_extractor",
        "games": fact_games,
        "errors": errors,
    }
    write_json(output_path, output_payload)

    log_end(
        "extract_facts",
        f"fact_games={len(fact_games)} errors={len(errors)} output={output_path}",
    )


if __name__ == "__main__":
    main()
