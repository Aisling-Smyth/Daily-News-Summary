import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

from config import *
from data_types import Story, StoryCluster, SummaryEntry
from email_utils import send_newsletter_email
from fetch import fetch
from cluster import cluster
from rank import rank
from summarise import summarise
from newsletter import build_newsletter_title, render, render_overview

logger = logging.getLogger(__name__)


def generate_newsletter(today: str) -> str:
    all_sections: List[str] = []
    section_meta: List[tuple[str, List[SummaryEntry]]] = []
    top_stories: List[SummaryEntry] = []

    for name, feeds in [
        ("🇮🇪 Ireland", IRISH_FEEDS),
        ("🇬🇧 UK", UK_FEEDS),
        ("🇺🇸 US", US_FEEDS),
        ("🌍 World", WORLD_FEEDS),
        ("🎬 Pop Culture", POP_CULTURE_FEEDS)
    ]:
        logger.info(f"Processing {name}...")
        stories = fetch(feeds, name)
        logger.info(f"Fetched {len(stories)} stories for {name}")

        if not stories:
            logger.warning(f"No stories found for {name}")
            continue

        clusters = rank(cluster(stories))
        logger.info(f"Created {len(clusters)} clusters for {name}")

        summaries = []
        max_summaries = 3
        for i, c in enumerate(clusters[:max_summaries]):
            try:
                headline = c[0].get("title", "Untitled story") if c else "Untitled story"
                summary_text = summarise(c)
                summary_entry: SummaryEntry = {
                    "headline": headline,
                    "summary": summary_text,
                    "link": c[0].get("link", ""),
                }
                summaries.append(summary_entry)
                if len(top_stories) < 3:
                    top_stories.append(summary_entry)
                logger.info(f"Summarized cluster {i+1}/{min(max_summaries, len(clusters))} for {name}")
            except Exception as e:
                logger.error(f"Failed to summarize cluster {i+1} for {name}: {e}", exc_info=True)
                continue

        if summaries:
            section_meta.append((name, summaries))
            all_sections.append(render(name, summaries))
            logger.info(f"Completed {name} with {len(summaries)} summaries")

    newsletter = render_overview(today, section_meta) + "\n\n" + "\n\n".join(all_sections) + "\n\n" + quote_of_the_day()
    return newsletter

def quote_of_the_day():
    import feedparser
    
    feed = feedparser.parse("https://www.brainyquote.com/link/quotebr.rss")

    if not feed.entries:
        return "<p>No quote available.</p>"

    entry = feed.entries[0]

    author = entry.title
    quote = entry.description

    return f"""
## Quote of the Day

*{quote}*

**— {author}**
"""

def main():
    parser = argparse.ArgumentParser(description="Generate the daily news summary newsletter.")
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Generate the newsletter without sending email even if SMTP settings are configured.",
    )
    parser.add_argument(
        "--attach",
        action="store_true",
        help="Attach the generated markdown file to the email when sending.",
    )
    args = parser.parse_args()

    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Output directory ready: {output_dir.absolute()}")
    logger.info(f"Logs directory ready: {logs_dir.absolute()}")
    logger.info(f"Log file: {log_file.absolute()}")

    try:
        newsletter = generate_newsletter(today)

        if not newsletter.strip():
            logger.warning("Newsletter is empty - no summaries were generated")
            logger.warning("Check that Ollama is running and gemma3 model is loaded")

        output_file = output_dir / f"daily_{today}.md"
        with open(output_file, "w", encoding="utf8") as f:
            f.write(newsletter)

        logger.info(f"Newsletter written to {output_file.absolute()}")

        subject = build_newsletter_title(today)
        send_email = EMAIL_SEND_ENABLED and not args.no_email
        if send_email:
            email_success = send_newsletter_email(
                newsletter,
                output_file if args.attach else None,
                subject=subject,
            )
            if not email_success:
                logger.error("Newsletter generation completed, but email failed.")
            else:
                logger.info("Newsletter emailed successfully.")
        elif args.no_email:
            logger.info("Email sending skipped by user request (--no-email).")
        elif not EMAIL_SEND_ENABLED:
            logger.info("Email sending is disabled because SMTP is not fully configured.")

        if newsletter.strip():
            logger.info("Newsletter generation completed successfully")
        else:
            logger.warning("Newsletter generation completed but output is empty")

    except Exception as e:
        logger.error(f"Fatal error during newsletter generation: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
