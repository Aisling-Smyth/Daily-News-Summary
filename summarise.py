import logging
import re
from time import sleep
from typing import Any

import requests

from config import (
    OLLAMA_MAX_RETRIES,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_URL,
)
from data_types import StoryCluster


logger = logging.getLogger(__name__)


def sanitize_summary_output(
    text: str,
) -> str:
    """
    Clean and normalise LLM output.

    Args:
        text:
            Raw model response.

    Returns:
        Clean markdown-friendly summary.
    """

    if not text:
        return ""

    cleaned = (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .strip()
    )

    cleaned = re.sub(
        r"```[\w-]*",
        "",
        cleaned,
    )

    cleaned = cleaned.replace(
        "**",
        "",
    )

    removal_patterns = [
        (
            r"(?im)^\s*"
            r"(okay|here(?:'s| is)|this is|"
            r"based on the headline provided|"
            r"would you like.*)"
            r".*$"
        ),
        r"(?im)^\s*(?:---|[-*_]{3,})\s*$",
    ]

    for pattern in removal_patterns:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
        )

    cleaned = re.sub(
        r"(?im)^\s*"
        r"(headline|summary|why it matters)"
        r"\s*:\s*",
        "",
        cleaned,
    )

    cleaned = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned,
    )

    return cleaned.strip()


def build_prompt(
    cluster: StoryCluster,
) -> str:
    """
    Build summarisation prompt from grouped stories.
    """

    headlines = "\n".join(
        f"- {story['source']}: {story['title']}"
        for story in cluster
    )

    return f"""
Summarise this news story as a concise but complete overview for a daily news digest.

Write two short paragraphs in plain prose.

The first paragraph should cover the main facts.
The second paragraph should explain why it matters and any wider implications.

Keep the tone factual and neutral.

Do not use:
- headings
- bullet points
- greetings
- preambles
- commentary about the writing process

Stories:

{headlines}
""".strip()


def summarise(
    cluster: StoryCluster,
) -> str:
    """
    Summarise a cluster of related news stories.

    Args:
        cluster:
            Related stories from multiple sources.

    Returns:
        Generated summary text.
    """

    prompt = build_prompt(
        cluster
    )

    return send_prompt(
        prompt
    )


def send_prompt(
    prompt: str,
) -> str:
    """
    Send prompt to Ollama.

    Args:
        prompt:
            Prompt text.

    Returns:
        Model response.

    Raises:
        Exception:
            If Ollama cannot complete the request.
    """

    for attempt in range(
        1,
        OLLAMA_MAX_RETRIES + 1,
    ):
        try:
            logger.debug(
                "Sending request to Ollama "
                "attempt %d/%d",
                attempt,
                OLLAMA_MAX_RETRIES,
            )

            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=OLLAMA_TIMEOUT,
            )

            response.raise_for_status()

            data: Any = response.json()

            if "response" not in data:
                raise ValueError(
                    "Unexpected Ollama response format"
                )

            return sanitize_summary_output(
                data["response"]
            )

        except requests.exceptions.ConnectionError:
            logger.error(
                "Could not connect to Ollama"
            )

        except requests.exceptions.Timeout:
            logger.error(
                "Ollama request timed out"
            )

        except requests.exceptions.RequestException:
            logger.error(
                "Ollama request failed",
                exc_info=True,
            )
            raise

        except ValueError:
            logger.error(
                "Invalid Ollama response",
                exc_info=True,
            )
            raise

        if attempt < OLLAMA_MAX_RETRIES:
            wait = 2 ** attempt

            logger.info(
                "Retrying Ollama in %d seconds",
                wait,
            )

            sleep(wait)

    raise RuntimeError(
        "Ollama unavailable after retries"
    )