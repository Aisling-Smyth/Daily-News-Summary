import feedparser
import logging
import requests
import urllib3
from time import sleep
from typing import List

from data_types import Story

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# User-Agent header to avoid being blocked by news websites
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def fetch(feeds: List[str], category: str) -> List[Story]:
    """Fetch stories from multiple RSS feeds with rate limiting and error handling.

    Args:
        feeds: List of RSS feed URLs.
        category: Category name for these feeds (for logging and data).

    Returns:
        List[Story]: Parsed story objects from all feeds.
    """
    stories: List[Story] = []

    for i, url in enumerate(feeds):
        try:
            logger.info(f"Fetching {url}...")
            
            # Fetch the feed content with proper headers and timeout
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "application/rss+xml, application/atom+xml, text/xml",
            }
            # Disable SSL verification for problematic feeds
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            
            # Parse the fetched content
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                logger.warning(f"No entries found in {url}")
                continue
            
            source = feed.feed.get("title", url)
            logger.debug(f"Feed source: {source}")

            feed_stories = 0
            for e in feed.entries[:10]:
                try:
                    story: Story = {
                        "title": getattr(e, "title", "[No title]"),
                        "summary": getattr(e, "summary", ""),
                        "link": getattr(e, "link", ""),
                        "source": source,
                        "category": category,
                    }
                    stories.append(story)
                    feed_stories += 1
                except Exception as e:
                    logger.warning(f"Failed to parse story from {source}: {e}")
                    continue

            logger.info(f"Fetched {feed_stories} stories from {source}")
            
            # Rate limiting: wait between feed requests
            if i < len(feeds) - 1:
                sleep(1)
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching {url} (waited 10s)")
            continue
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error while fetching {url}: {e}")
            continue
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL error while fetching {url}: {e}")
            continue
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error while fetching {url}: {e.response.status_code}")
            continue
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            continue
    
    logger.info(f"Total stories fetched for {category}: {len(stories)}")
    return stories