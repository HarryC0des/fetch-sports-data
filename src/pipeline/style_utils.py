def normalize_style(value):
    if not value:
        return "mix"
    normalized = value.strip().lower()
    normalized = normalized.replace("-", " ")
    normalized = " ".join(normalized.split())
    if normalized in ("hot take", "hot takes"):
        return "hot_takes"
    if normalized in ("fact", "factual"):
        return "factual"
    if normalized in ("analysis", "analytical"):
        return "analytical"
    if normalized in ("nuance", "nuanced"):
        return "nuanced"
    if normalized in ("mix", "mixed"):
        return "mix"
    return normalized.replace(" ", "_")


def style_label(style_key):
    labels = {
        "factual": "Factual",
        "hot_takes": "Hot Takes",
        "analytical": "Analytical",
        "nuanced": "Nuanced",
        "mix": "Mix",
    }
    return labels.get(style_key, style_key.title())
