import logging
from datetime import datetime
from typing import List, Sequence

logger = logging.getLogger(__name__)


def build_section_overview(items: Sequence[dict]) -> str:
    """Create a short overview for a section from its top headlines."""
    if not items:
        return "This section covers the latest developments in the region."

    headlines = [item.get("headline", "") for item in items[:3] if item.get("headline")]
    if not headlines:
        return "This section covers the latest developments in the region."

    if len(headlines) == 1:
        return f"This section focuses on {headlines[0]}."

    if len(headlines) == 2:
        return f"This section focuses on {headlines[0]} and {headlines[1]}."

    return f"This section focuses on {headlines[0]}, {headlines[1]}, and {headlines[2]}."


def build_newsletter_title(today: str) -> str:
    """Build the newsletter title and email subject from a date string."""
    date_text = datetime.strptime(today, "%Y-%m-%d").strftime("%d %B %Y")
    return f"Daily News Summary: {date_text}"


def render_overview(today: str, sections: Sequence[tuple[str, list[dict]]], top_stories: Sequence[dict]) -> str:
    """Render a polished overview for the newsletter."""
    title = build_newsletter_title(today)
    lines = [
        f"# {title}",
        "",
        "## Table of contents",
        "",
    ]

    for name, items in sections:
        anchor = name.lower().replace("🇮🇪", "ireland").replace("🇺🇸", "us").replace("🌍", "world").replace(" ", "-")
        lines.append(f"- [{name}](#{anchor})")
        lines.append(f"  - [Overview](#{anchor}-overview)")
        for i, item in enumerate(items[:5], 1):
            sub_anchor = f"{anchor}-{i}"
            headline = item.get("headline", f"Story {i}")
            lines.append(f"  - [{headline}]({anchor}#{sub_anchor})")

    lines.extend(["", "---", ""])
    return "\n".join(lines)


def render(name: str, summaries: Sequence[dict]) -> str:
    """Render newsletter section with summaries.

    Args:
        name: Section name (e.g., "🇮🇪 Ireland").
        summaries: List of summary dictionaries.

    Returns:
        str: Formatted markdown section.
    """
    if not summaries:
        logger.warning(f"No summaries to render for {name}")
        return ""

    overview = build_section_overview(summaries)
    out = [f"## {name}", "", f"### Overview", "", f"{overview}", "", ""]
    anchor = name.lower().replace("🇮🇪", "ireland").replace("🇺🇸", "us").replace("🌍", "world").replace(" ", "-")
    out[0] = f"## {name}"
    out.insert(1, "")
    out.insert(2, f"<a id=\"{anchor}-overview\"></a>")

    for i, item in enumerate(summaries[:5], 1):
        if isinstance(item, dict):
            headline = item.get("headline", f"Story {i}")
            summary_text = item.get("summary", "")
            link = item.get("link", "")
        else:
            headline = f"Story {i}"
            summary_text = item
            link = ""

        out.append(f"### {headline}")
        out.append("")
        out.append(summary_text)
        if link:
            out.append("")
            out.append(f"[Read full article]({link})")
        out.append("")
        out.append("---")
        out.append("")

    result = "\n".join(out)
    logger.debug(f"Rendered {len(summaries)} summaries for {name}")
    return result