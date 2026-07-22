"""
Quote retrieval for the newsletter.

Kept separate from newsletter generation so the quote source
can be changed independently of the rest of the pipeline.
"""

import logging

import feedparser

from config import QUOTE_FEED_URL


logger = logging.getLogger(__name__)


def quote_of_the_day() -> str:
    """
    Fetch and format the quote of the day.

    Returns:
        Markdown formatted quote section.
    """

    try:
        feed = feedparser.parse(
            QUOTE_FEED_URL
        )

        if not feed.entries:
            logger.warning(
                "No quote found"
            )
            return ""

        entry = feed.entries[0]

        author = getattr(
            entry,
            "title",
            "Unknown",
        )

        quote = getattr(
            entry,
            "description",
            "",
        )

        if not quote:
            return ""

        return f"""
## Quote of the Day

*{quote}*

**— {author}**
"""

    except Exception:
        logger.error(
            "Failed to retrieve quote of the day",
            exc_info=True,
        )
        return ""