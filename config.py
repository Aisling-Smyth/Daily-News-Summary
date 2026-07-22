import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# Email
# ============================================================

SMTP_SERVER = os.environ.get(
    "SMTP_SERVER",
    "",
)

SMTP_PORT = int(
    os.environ.get(
        "SMTP_PORT",
        "587",
    )
)

SMTP_USERNAME = os.environ.get(
    "SMTP_USERNAME",
    "",
)

SMTP_PASSWORD = os.environ.get(
    "SMTP_PASSWORD",
    "",
)

EMAIL_FROM = os.environ.get(
    "EMAIL_FROM",
    SMTP_USERNAME,
)

EMAIL_TO = [
    addr.strip()
    for addr in os.environ.get(
        "EMAIL_TO",
        "",
    ).split(",")
    if addr.strip()
]

EMAIL_SUBJECT = os.environ.get(
    "EMAIL_SUBJECT",
    "Daily News Summary",
)

EMAIL_USE_TLS = (
    os.environ.get(
        "EMAIL_USE_TLS",
        "true",
    )
    .strip()
    .lower()
    in (
        "1",
        "true",
        "yes",
        "y",
    )
)

EMAIL_SEND_ENABLED = bool(
    SMTP_SERVER
    and SMTP_USERNAME
    and SMTP_PASSWORD
    and EMAIL_TO
)


# ============================================================
# Ollama
# ============================================================

OLLAMA_URL = os.environ.get(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate",
)

OLLAMA_MODEL = os.environ.get(
    "OLLAMA_MODEL",
    "gemma3:latest",
)

OLLAMA_TIMEOUT = int(
    os.environ.get(
        "OLLAMA_TIMEOUT",
        "120",
    )
)

OLLAMA_MAX_RETRIES = int(
    os.environ.get(
        "OLLAMA_MAX_RETRIES",
        "3",
    )
)


# ============================================================
# Newsletter
# ============================================================

MAX_SUMMARIES_PER_SECTION = int(
    os.environ.get(
        "MAX_SUMMARIES_PER_SECTION",
        "3",
    )
)

QUOTE_FEED_URL = os.environ.get(
    "QUOTE_FEED_URL",
    "https://www.brainyquote.com/link/quotebr.rss",
)


# ============================================================
# RSS fetching
# ============================================================

REQUEST_TIMEOUT = int(
    os.environ.get(
        "REQUEST_TIMEOUT",
        "30",
    )
)

MAX_ENTRIES_PER_FEED = int(
    os.environ.get(
        "MAX_ENTRIES_PER_FEED",
        "10",
    )
)

RATE_LIMIT_SECONDS = float(
    os.environ.get(
        "RATE_LIMIT_SECONDS",
        "1",
    )
)


# ============================================================
# Clustering
# ============================================================

EMBEDDING_MODEL = os.environ.get(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2",
)

CLUSTER_EPS = float(
    os.environ.get(
        "CLUSTER_EPS",
        "0.35",
    )
)

CLUSTER_MIN_SAMPLES = int(
    os.environ.get(
        "CLUSTER_MIN_SAMPLES",
        "1",
    )
)