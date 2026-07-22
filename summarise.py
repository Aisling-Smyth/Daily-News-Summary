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
from prompt_utils import load_prompt


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
        Clean summary text.
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
    Build summary prompt from story cluster.

    Args:
        cluster:
            Related news stories.

    Returns:
        Completed prompt.
    """

    headlines = "\n".join(
        f"- {story['source']}: {story['title']}"
        for story in cluster
    )

    template = load_prompt(
        "summary.txt"
    )

    return template.format(
        headlines=headlines,
    )


def summarise(
    cluster: StoryCluster,
) -> str:
    """
    Summarise a cluster of related stories.

    Args:
        cluster:
            Related news stories.

    Returns:
        Generated summary.
    """

    return send_prompt(
        build_prompt(cluster)
    )


def send_prompt(
    prompt: str,
) -> str:
    """
    Send prompt to Ollama.

    Args:
        prompt:
            Prompt sent to model.

    Returns:
        Cleaned model response.

    Raises:
        RuntimeError:
            If Ollama is unavailable after retries.
    """

    for attempt in range(
        1,
        OLLAMA_MAX_RETRIES + 1,
    ):
        try:
            logger.debug(
                "Calling Ollama (%s), attempt %d/%d",
                OLLAMA_MODEL,
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

            if response.status_code >= 400:
                logger.error(
                    "Ollama returned HTTP %s",
                    response.status_code,
                )
                logger.error(
                    "Ollama response body: %s",
                    response.text,
                )

            response.raise_for_status()

            data: Any = response.json()

            if "response" not in data:
                raise ValueError(
                    f"Unexpected Ollama response: {data}"
                )

            return sanitize_summary_output(
                data["response"]
            )

        except requests.exceptions.ConnectionError as e:
            logger.error(
                "Could not connect to Ollama: %s",
                e,
            )

        except requests.exceptions.Timeout as e:
            logger.error(
                "Ollama timeout: %s",
                e,
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
            delay = 2 ** attempt

            logger.info(
                "Retrying Ollama in %s seconds",
                delay,
            )

            sleep(delay)

    raise RuntimeError(
        "Ollama unavailable after retries"
    )