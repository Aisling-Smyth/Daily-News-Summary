import logging
from time import sleep
from typing import List

import feedparser
import requests

from config import (
    MAX_ENTRIES_PER_FEED,
    RATE_LIMIT_SECONDS,
    REQUEST_TIMEOUT,
)
from data_types import Story


logger = logging.getLogger(__name__)


USER_AGENT = (
    "Mozilla/5.0 "
    "(Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/120 Safari/537.36"
)


def fetch(
    feeds: List[str],
    category: str,
) -> List[Story]:
    """
    Fetch stories from RSS feeds.

    Args:
        feeds:
            List of RSS feed URLs.

        category:
            Newsletter section name.

    Returns:
        List of parsed stories.
    """

    stories: List[Story] = []

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": (
            "application/rss+xml, "
            "application/atom+xml, "
            "text/xml"
        ),
    }

    session = requests.Session()
    session.headers.update(headers)

    for index, url in enumerate(feeds):

        try:
            logger.info(
                "Fetching feed %d/%d for %s",
                index + 1,
                len(feeds),
                category,
            )

            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            feed = feedparser.parse(
                response.content
            )

            if not feed.entries:
                logger.warning(
                    "No entries found in feed: %s",
                    url,
                )
                continue

            source = feed.feed.get(
                "title",
                url,
            )

            count = 0

            for entry in feed.entries[:MAX_ENTRIES_PER_FEED]:

                story: Story = {
                    "title": getattr(
                        entry,
                        "title",
                        "[No title]",
                    ),
                    "summary": getattr(
                        entry,
                        "summary",
                        "",
                    ),
                    "link": getattr(
                        entry,
                        "link",
                        "",
                    ),
                    "source": source,
                    "category": category,
                }

                stories.append(
                    story
                )

                count += 1

            logger.info(
                "Fetched %d stories from %s",
                count,
                source,
            )

        except requests.exceptions.Timeout:
            logger.error(
                "Timeout fetching feed: %s",
                url,
            )

        except requests.exceptions.HTTPError as exc:
            logger.error(
                "HTTP error fetching %s: %s",
                url,
                exc.response.status_code,
            )

        except requests.exceptions.RequestException as exc:
            logger.error(
                "Request error fetching %s: %s",
                url,
                exc,
            )

        except Exception:
            logger.error(
                "Unexpected error fetching %s",
                url,
                exc_info=True,
            )

        finally:
            if index < len(feeds) - 1:
                sleep(
                    RATE_LIMIT_SECONDS
                )

    logger.info(
        "Fetched %d total stories for %s",
        len(stories),
        category,
    )

    return stories