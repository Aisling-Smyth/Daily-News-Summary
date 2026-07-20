import os

SMTP_SERVER = os.environ.get("SMTP_SERVER", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", SMTP_USERNAME)
EMAIL_TO = [addr.strip() for addr in os.environ.get("EMAIL_TO", "").split(",") if addr.strip()]
EMAIL_SUBJECT = os.environ.get("EMAIL_SUBJECT", "Daily News Summary")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").strip().lower() in ("1", "true", "yes", "y")
EMAIL_SEND_ENABLED = bool(SMTP_SERVER and SMTP_USERNAME and SMTP_PASSWORD and EMAIL_TO)

IRISH_FEEDS = [
    "https://www.rte.ie/feeds/rss/?index=/news/",
    "https://www.independent.ie/irish-news/rss/",
    "https://www.rte.ie/feeds/rss/?index=/news/world/",
    "https://www.bbc.co.uk/news/world/rss.xml",
    "https://feeds.theguardian.com/theguardian/rss",
]

US_FEEDS = [
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.foxnews.com/foxnews/latest",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://www.washingtonpost.com/rss",
]

WORLD_FEEDS = [
    "https://www.bbc.co.uk/news/world/rss.xml",
    "https://www.france24.com/en/rss",
    "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://feeds.theguardian.com/theguardian/rss",
]

POP_CULTURE_FEEDS = [
    "https://www.bbc.co.uk/news/entertainment_and_arts/rss.xml",
    "https://deadline.com/feed/",
    "https://www.hollywoodreporter.com/feed/",
    "https://variety.com/feed/",
    "https://www.comingsoon.net/feed",
]