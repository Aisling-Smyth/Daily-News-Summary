import logging
import re
from time import sleep
from typing import List

import requests

from data_types import Story, StoryCluster

logger = logging.getLogger(__name__)

URL = "http://localhost:11434/api/generate"
MODEL = "gemma3"
TIMEOUT = 120  # seconds
MAX_RETRIES = 3


def sanitize_summary_output(text):
    """Normalize LLM output to a concise factual format."""
    if not text:
        return ""

    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = re.sub(r"```[\w-]*", "", cleaned)
    cleaned = cleaned.replace("**", "")

    removal_patterns = [
        r"(?im)^\s*(okay|here(?:'s| is)|this is|based on the headline provided|aiming for neutrality and conciseness|remain neutral and concise|would you like me to|would you like|please let me know|thanks for providing|i can help).*$",
        r"(?im)^\s*(?:---|[-*_]{3,})\s*$",
    ]
    for pattern in removal_patterns:
        cleaned = re.sub(pattern, "", cleaned)

    cleaned = re.sub(r"(?im)^\s*(headline|summary|why it matters)\s*:\s*", "", cleaned)
    cleaned = re.sub(r"\n{2,}", "\n\n", cleaned).strip()

    return cleaned


def summarise(cluster: StoryCluster) -> str:
    """Summarize a cluster of news stories using Ollama.

    Args:
        cluster: List of story dicts with 'source' and 'title' keys.

    Returns:
        str: Generated summary from the LLM.

    Raises:
        Exception: If Ollama service is unavailable or LLM fails.
    """
    headlines = "\n".join(
        f"- {s['source']}: {s['title']}"
        for s in cluster
    )

    prompt = f"""Summarise this news story as a concise but complete overview for a daily news digest.

Write two short paragraphs and keep the tone factual and neutral.
Use plain prose, not bullet points or headings.
The first paragraph should cover the main facts of the story.
The second paragraph should explain why the story matters and any wider implications.

Do not use preambles, greetings, questions, markdown, or extra commentary.

Headlines:

{headlines}
"""
    return send_prompt(prompt)

def send_prompt(prompt):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug(f"Sending request to Ollama (attempt {attempt}/{MAX_RETRIES})")
            r = requests.post(
                URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=TIMEOUT,
            )
            r.raise_for_status()

            response = r.json()
            if "response" not in response:
                raise ValueError(f"Unexpected Ollama response format: {response}")

            summary_text = sanitize_summary_output(response["response"])
            logger.debug("Successfully summarized cluster")
            return summary_text
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection failed to Ollama at {URL}: {e}")
            if attempt < MAX_RETRIES:
                wait_time = 2 ** attempt  # exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                sleep(wait_time)
            else:
                logger.error(f"Failed to connect to Ollama after {MAX_RETRIES} attempts")
                raise
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling Ollama after {TIMEOUT}s")
            if attempt < MAX_RETRIES:
                logger.info(f"Retrying (attempt {attempt+1}/{MAX_RETRIES})...")
                sleep(2)
            else:
                raise
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise
        
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid response from Ollama: {e}")
            raise