import logging
from datetime import datetime
from typing import List, Sequence
from summarise import send_prompt

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


def render_overview(today: str, sections: Sequence[tuple[str, list[dict]]]) -> str:
    """Render a polished overview for the newsletter."""
    title = build_newsletter_title(today)

    blurb = send_prompt(f"""You are writing the opening blurb for a casual newsletter called "Up Smyth Creek", where you greet your friends with a witty introduction.

The audience is a small group of friends.

Write 1-3 sentences (40-70 words).

The tone should be witty, dry, slightly sarcastic, and conversational—not cringe, not overly enthusiastic, and not like a journalist. It should sound like someone opening the conversation in a group chat.

Reference the overall mix of today's stories (below) without mentioning every headline. If there are obvious themes (politics, storms, celebrity drama, AI, sports, etc.), weave them into the joke.

Avoid:
- "In today's fast-paced world..."
- "Buckle up..."
- "Here's everything you need to know..."
- excessive emojis
- clichés
- corporate newsletter language
                        
Your humour is:
- Irish
- dry
- observational
- slightly sarcastic
- never mean
- occasionally self-deprecating

Today's stories: {sections}
""")

    lines = [
        f"# {title}",
        "",
        f"{blurb}",
        "",
        "## Table of contents",
        "",
    ]

    for name, _ in sections:
        lines.append(f"- {name}")

    lines.extend([
        "",
        "---",
        "",
    ])

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

    out = [f"## {name}"]

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