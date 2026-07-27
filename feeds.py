"""
RSS feed sources used by the newsletter.

Keeping feeds separate from configuration means
sources can be changed without touching runtime settings.
"""

from typing import List, Tuple


IRISH_FEEDS: List[str] = [
    "https://www.rte.ie/feeds/rss/?index=/news/",
    "https://feeds.feedburner.com/ieireland",
    "https://www.independent.ie/irish-news/rss/",
    "https://feeds.breakingnews.ie/bntopstories?format=xml",
    "https://www.thejournal.ie/feed/",
    "https://limerickleader.ie/rss",
]


UK_FEEDS: List[str] = [
    "https://feeds.skynews.com/feeds/rss/home.xml",
    "https://www.independent.co.uk/news/uk/rss",
    "https://www.huffingtonpost.co.uk/feeds/index.xml",
    "https://www.dailyrecord.co.uk/news/?service=rss",
    "https://feeds.bbci.co.uk/news/uk/rss.xml",
]


US_FEEDS: List[str] = [
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.washingtonpost.com/rss/national",
    "https://feeds.washingtonpost.com/rss/politics",
    "https://www.cbsnews.com/latest/rss/us",
    "https://abcnews.com/abcnews/usheadlines",
    "https://abcnews.com/abcnews/politicsheadlines",
]


WORLD_FEEDS: List[str] = [
    "https://www.bbc.co.uk/news/world/rss.xml",
    "https://www.rte.ie/feeds/rss/?index=/news/world/",
    "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "https://feeds.theguardian.com/theguardian/rss",
    "https://feeds.washingtonpost.com/rss/world",
    "https://feeds.feedburner.com/ieworld",
    "https://www.cbsnews.com/latest/rss/world",
    "https://abcnews.com/abcnews/internationalheadlines",
    "https://www.independent.co.uk/news/world/rss",
]


POP_CULTURE_FEEDS: List[str] = [
    "https://www.bbc.co.uk/news/entertainment_and_arts/rss.xml",
    "https://deadline.com/feed/",
    "https://www.hollywoodreporter.com/feed/",
    "https://variety.com/feed/",
    "https://www.comingsoon.net/feed",
    "https://feeds.feedburner.com/ielifestyle",
    "https://www.cbsnews.com/latest/rss/entertainment",
    "https://abcnews.com/abcnews/entertainmentheadlines",
]

TECH_FEEDS: List[str] = [
    "https://www.wired.com/feed/tag/ai/latest/rss",
    "https://aifornewsroom.in/api/rss",
    "https://www.theverge.com/rss/index.xml",
    "https://arstechnica.com/ai/feed/",
    "https://techcrunch.com/feed/",
]

SECTIONS: List[Tuple[str, str, List[str]]] = [
    ("Ireland", "🇮🇪", IRISH_FEEDS),
    ("UK", "🇬🇧", UK_FEEDS),
    ("US", "🇺🇸", US_FEEDS),
    ("World", "🌍", WORLD_FEEDS),
    ("Pop Culture", "🎬", POP_CULTURE_FEEDS),
    ("Tech and AI", "🤖", TECH_FEEDS),
]