import logging
from datetime import datetime
from typing import List, Sequence, Tuple

from data_types import SummaryEntry
from prompt_utils import load_prompt
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
        item.get("headline", "")
        for item in items[:3]
        if item.get("headline")
    ]

    if not headlines:
        return "This section covers the latest developments."

    return "; ".join(headlines)


def clean_intro_output(
    text: str,
) -> str:
    """
    Remove common LLM formatting artefacts.

    Args:
        text:
            Raw generated introduction.

    Returns:
        Clean introduction text.
    """

    if not text:
        return ""

    cleaned = text.strip()

    prefixes = [
        "alright, here's a blurb draft:",
        "here's a blurb draft:",
        "here is a blurb draft:",
        "sure,",
        "of course,",
        "certainly,",
    ]

    lower = cleaned.lower()

    for prefix in prefixes:
        if lower.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break

    if (
        cleaned.startswith('"')
        and cleaned.endswith('"')
    ):
        cleaned = cleaned[1:-1].strip()

    if (
        cleaned.startswith("'")
        and cleaned.endswith("'")
    ):
        cleaned = cleaned[1:-1].strip()

    return cleaned


def render_overview(
    today: str,
    sections: Sequence[
        Tuple[str, List[SummaryEntry]]
    ],
) -> str:
    """
    Render newsletter introduction and contents.

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
        f"{name}: {build_section_overview(items)}"
        for name, items in sections
    )

    prompt = load_prompt(
        "newsletter_intro.txt"
    )

    blurb = send_prompt(
        prompt.format(
            sections=section_context,
        )
    )

    blurb = clean_intro_output(
        blurb
    )

    lines = [
        f"# {title}",
        "",
        blurb,
        "",
        "## Table of contents",
        "",
    ]

    for name, feeds in sections:
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
        headline = item.get(
            "headline",
            f"Story {index}",
        )

        output.append(
            f"### {headline}"
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