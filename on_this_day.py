import logging
import random
import re
from datetime import date
from typing import List, TypedDict, Optional

import requests
from dotenv import load_dotenv
import os

import holidays  # Checkiday's official client — collides in name with the
                  # unrelated PyPI "holidays" package if both are installed

from config import ON_THIS_DAY_TIMEOUT
from prompt_utils import load_prompt
from summarise import send_prompt  # reuse existing Ollama plumbing

load_dotenv()

logger = logging.getLogger(__name__)


class OnThisDayFact(TypedDict):
    year: str
    text: str


class FunDayEvent(TypedDict):
    name: str
    url: Optional[str]


# ---------- Historical facts (Wikipedia via muffinlabs) ----------

# Heuristic only — used to bucket candidates for tone *balance*,
# not to exclude anything. Every event is still eligible to be used;
# this just helps us draw from a mix of heavier/lighter facts rather
# than an all-one-tone set by chance.
_HEAVY_KEYWORDS = re.compile(
    r"\b(died|death|killed|assassinat\w*|war|battle|bomb\w*|"
    r"massacre|earthquake|disaster|attack|execut\w*|genocide|"
    r"crash|explosion|famine|plague)\b",
    re.IGNORECASE,
)


def fetch_on_this_day_events(
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> List[OnThisDayFact]:
    """
    Fetch historical "on this day" events from muffinlabs' free API.

    Args:
        month:
            Month to query (defaults to today).
        day:
            Day to query (defaults to today).

    Returns:
        List of raw events, each with "year" and "text".
        Empty list if the request fails.
    """

    today = date.today()
    month = month or today.month
    day = day or today.day

    try:
        response = requests.get(
            f"https://history.muffinlabs.com/date/{month}/{day}",
            timeout=ON_THIS_DAY_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        return [
            {"year": event["year"], "text": event["text"]}
            for event in data["data"]["Events"]
        ]

    except requests.exceptions.RequestException as e:
        logger.error("Could not fetch on-this-day events: %s", e)
        return []

    except (KeyError, ValueError) as e:
        logger.error("Unexpected on-this-day API response: %s", e)
        return []


def _split_by_weight(
    events: list[OnThisDayFact],
) -> tuple[list[OnThisDayFact], list[OnThisDayFact]]:
    """Bucket events into (heavier, lighter) by keyword heuristic."""

    heavier = [e for e in events if _HEAVY_KEYWORDS.search(e["text"])]
    lighter = [e for e in events if not _HEAVY_KEYWORDS.search(e["text"])]

    return heavier, lighter


def _pick_balanced(
    events: list[OnThisDayFact],
    count: int,
) -> list[OnThisDayFact]:
    """
    Pick `count` distinct facts, aiming for a mix of heavier/lighter
    where both are available.
    """

    heavier, lighter = _split_by_weight(events)
    random.shuffle(heavier)
    random.shuffle(lighter)

    picks: list[OnThisDayFact] = []

    while len(picks) < count and (heavier or lighter):
        if heavier:
            picks.append(heavier.pop())
        if len(picks) < count and lighter:
            picks.append(lighter.pop())

    return picks[:count]


def build_on_this_day_prompt(fact: OnThisDayFact) -> str:
    """Build rewrite prompt for a single historical fact."""

    template = load_prompt("on_this_day.txt")
    return template.format(year=fact["year"], text=fact["text"])


def _rewrite_historical_fact(fact: OnThisDayFact) -> Optional[str]:
    """Rewrite a single historical fact via the model."""

    try:
        return send_prompt(build_on_this_day_prompt(fact))
    except RuntimeError:
        logger.error("Ollama unavailable while generating historical blurb")
        return None


def get_historical_blurbs(count: int = 3) -> list[str]:
    """
    Fetch and rewrite `count` historical "on this day" facts, aiming
    for a mix of heavier and lighter events where possible.
    """

    events = fetch_on_this_day_events()

    if not events:
        return []

    picks = _pick_balanced(events, count)

    return [
        blurb
        for fact in picks
        if (blurb := _rewrite_historical_fact(fact)) is not None
    ]


# ---------- Fun/quirky observances (Checkiday) ----------


def fetch_fun_day_events() -> list[FunDayEvent]:
    """
    Fetch today's fun/quirky observances from Checkiday via the
    official client library.

    Returns:
        List of events, each with "name" and "url". Empty list on
        failure — caller should handle this gracefully.
    """

    try:
        client = holidays.client(os.environ["CHECKIDAY_API_KEY"])
        response = client.getEvents()  # free plan: no timezone override
        return [
            {"name": e.name, "url": e.url}
            for e in response.events
        ]
    except Exception as e:
        logger.error("Checkiday request failed: %s", e)
        return []


def build_fun_day_prompt(event: FunDayEvent) -> str:
    """Build rewrite prompt for a single fun-day observance."""

    template = load_prompt("fun_day.txt")
    return template.format(name=event["name"])


def _rewrite_fun_day(event: FunDayEvent) -> Optional[str]:
    """Rewrite a single fun-day observance via the model."""

    try:
        return send_prompt(build_fun_day_prompt(event))
    except RuntimeError:
        logger.error("Ollama unavailable while generating fun-day blurb")
        return None


def get_fun_day_blurbs(count: int = 2) -> list[str]:
    """
    Fetch and rewrite `count` fun/quirky observances for today.

    Some days return many events (7+); this picks a random subset
    rather than always using the first ones returned.
    """

    events = fetch_fun_day_events()

    if not events:
        return []

    picks = random.sample(events, k=min(count, len(events)))

    return [
        blurb
        for event in picks
        if (blurb := _rewrite_fun_day(event)) is not None
    ]


# ---------- Create cards ----------

def get_on_this_day_card(count: int = 3) -> list[str]:
    """Historical events for today's date."""
    return get_historical_blurbs(count)


def get_fun_days_card(count: int = 3) -> list[str]:
    """Today's quirky observances."""
    return get_fun_day_blurbs(count)


if __name__ == "__main__":
    for blurb in get_on_this_day_card():
        print(f"- {blurb}")