import logging
from datetime import datetime
from typing import List, Sequence, Tuple

from data_types import SummaryEntry
from summarise import send_prompt


logger = logging.getLogger(__name__)


def build_newsletter_title(
    today: str,
) -> str:
    """
    Build newsletter title from date.

    Args:
        today:
            Date in YYYY-MM-DD format.

    Returns:
        Formatted newsletter title.
    """

    date_text = datetime.strptime(
        today,
        "%Y-%m-%d",
    ).strftime(
        "%d %B %Y"
    )

    return f"Daily News Summary: {date_text}"


def build_section_overview(
    items: Sequence[SummaryEntry],
) -> str:
    """
    Create a short section description.

    Args:
        items:
            Section summaries.

    Returns:
        Human-readable overview.
    """

    headlines = [
        item["headline"]
        for item in items[:3]
        if item.get("headline")
    ]

    if not headlines:
        return (
            "This section covers "
            "the latest developments."
        )

    if len(headlines) == 1:
        return (
            f"This section focuses on "
            f"{headlines[0]}."
        )

    if len(headlines) == 2:
        return (
            f"This section focuses on "
            f"{headlines[0]} and {headlines[1]}."
        )

    return (
        f"This section focuses on "
        f"{headlines[0]}, {headlines[1]}, "
        f"and {headlines[2]}."
    )


def render_overview(
    today: str,
    sections: Sequence[
        Tuple[str, List[SummaryEntry]]
    ],
) -> str:
    """
    Render newsletter introduction.

    Args:
        today:
            Newsletter date.

        sections:
            Generated newsletter sections.

    Returns:
        Markdown introduction.
    """

    title = build_newsletter_title(
        today
    )

    section_context = "\n".join(
        f"{name}: "
        f"{build_section_overview(items)}"
        for name, items in sections
    )

    blurb = send_prompt(
        f"""
You are writing the opening blurb for a casual newsletter called "Up Smyth Creek".

The audience is a small group of friends.

Write 1-3 sentences (40-70 words).

Tone:
- Irish
- dry
- observational
- slightly sarcastic
- conversational

Avoid:
- corporate newsletter language
- clichés
- excessive enthusiasm
- "here's everything you need to know"

Today's sections:

{section_context}
""".strip()
    )

    lines = [
        f"# {title}",
        "",
        blurb,
        "",
        "## Table of contents",
        "",
    ]

    for name, _ in sections:
        lines.append(
            f"- {name}"
        )

    lines.extend(
        [
            "",
            "---",
            "",
        ]
    )

    return "\n".join(
        lines
    )


def render(
    name: str,
    summaries: Sequence[SummaryEntry],
) -> str:
    """
    Render a newsletter section.

    Args:
        name:
            Section title.

        summaries:
            Stories in this section.

    Returns:
        Markdown section.
    """

    if not summaries:
        logger.warning(
            "No summaries to render for %s",
            name,
        )
        return ""

    output = [
        f"## {name}",
        "",
    ]

    for index, item in enumerate(
        summaries,
        start=1,
    ):
        output.append(
            f"### {item.get('headline', f'Story {index}')}"
        )

        output.append(
            ""
        )

        output.append(
            item.get(
                "summary",
                "",
            )
        )

        link = item.get(
            "link",
            "",
        )

        if link:
            output.extend(
                [
                    "",
                    f"[Read full article]({link})",
                ]
            )

        output.extend(
            [
                "",
                "---",
                "",
            ]
        )

    logger.debug(
        "Rendered %d summaries for %s",
        len(summaries),
        name,
    )

    return "\n".join(
        output
    )