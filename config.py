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
    # "https://www.rte.ie/feeds/rss/?index=/news/",
    # "https://feeds.feedburner.com/ieireland", # Irish Examiner
    # "https://www.independent.ie/irish-news/rss/",
    # "https://feeds.breakingnews.ie/bntopstories?format=xml",
    # "https://www.thejournal.ie/feed/",
    # "https://limerickleader.ie/rss",
]

UK_FEEDS = [
    # "https://feeds.skynews.com/feeds/rss/home.xml",
    # "https://www.independent.co.uk/news/uk/rss",
    # "https://www.huffingtonpost.co.uk/feeds/index.xml",
    # "https://www.dailyrecord.co.uk/news/?service=rss",
    # "https://feeds.bbci.co.uk/news/uk/rss.xml",
]

US_FEEDS = [
    # "https://feeds.npr.org/1001/rss.xml",
    # "https://feeds.washingtonpost.com/rss/national",
    # "https://feeds.washingtonpost.com/rss/politics",
    # "https://www.cbsnews.com/latest/rss/us",
    # "https://abcnews.com/abcnews/usheadlines",
    # "https://abcnews.com/abcnews/politicsheadlines",
]

WORLD_FEEDS = [
    # "https://www.bbc.co.uk/news/world/rss.xml",
    # "https://www.rte.ie/feeds/rss/?index=/news/world/",
    # "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    # "https://feeds.theguardian.com/theguardian/rss",
    # "https://feeds.washingtonpost.com/rss/world",
    # "https://feeds.feedburner.com/ieworld", # Irish Examiner
    # "https://www.cbsnews.com/latest/rss/world",
    # "https://abcnews.com/abcnews/internationalheadlines",
    # "https://www.independent.co.uk/news/world/rss",
]

POP_CULTURE_FEEDS = [
    "https://www.bbc.co.uk/news/entertainment_and_arts/rss.xml",
    "https://deadline.com/feed/",
    "https://www.hollywoodreporter.com/feed/",
    "https://variety.com/feed/",
    "https://www.comingsoon.net/feed",
    "https://feeds.feedburner.com/ielifestyle",
    "https://www.cbsnews.com/latest/rss/entertainment",
    "https://abcnews.com/abcnews/entertainmentheadlines",
]