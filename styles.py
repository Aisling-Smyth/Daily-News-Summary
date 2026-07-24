from pathlib import Path


def load_styles() -> str:
    return Path(
        "styles/newsletter.css"
    ).read_text(
        encoding="utf-8"
    )