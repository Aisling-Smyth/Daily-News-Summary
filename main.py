import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from config import (
    EMAIL_SEND_ENABLED,
    MAX_SUMMARIES_PER_SECTION,
)
from data_types import SummaryEntry
from email_utils import send_newsletter_email
from fetch import fetch
from feeds import SECTIONS
from newsletter import (
    build_newsletter_title,
    render,
    render_overview,
)

from newsletter_html import render_newsletter_html
from quotes import quote_of_the_day
from cluster import cluster
from rank import rank
from summarise import summarise


logger = logging.getLogger(__name__)


def generate_section(
    name: str,
    feed_urls: List[str],
) -> Tuple[str, List[SummaryEntry]]:
    """
    Generate newsletter summaries for one section.

    Args:
        name:
            Display name of the section.

        feed_urls:
            RSS feeds for the section.

    Returns:
        Tuple containing section name and generated summaries.
    """

    logger.info("Processing %s...", name)

    stories = fetch(feed_urls, name)

    if not stories:
        logger.warning(
            "No stories found for %s",
            name,
        )
        return name, []

    clusters = rank(
        cluster(stories)
    )

    logger.info(
        "Created %d clusters for %s",
        len(clusters),
        name,
    )

    summaries: List[SummaryEntry] = []

    for index, story_cluster in enumerate(
        clusters[:MAX_SUMMARIES_PER_SECTION],
        start=1,
    ):
        try:
            summary = summarise(story_cluster)

            entry: SummaryEntry = {
                "headline": story_cluster[0].get(
                    "title",
                    "Untitled story",
                ),
                "summary": summary,
                "link": story_cluster[0].get(
                    "link",
                    "",
                ),
            }

            summaries.append(entry)

            logger.info(
                "Summarised story %d/%d for %s",
                index,
                MAX_SUMMARIES_PER_SECTION,
                name,
            )

        except Exception:
            logger.error(
                "Failed summarising story %d for %s",
                index,
                name,
                exc_info=True,
            )

    return name, summaries


def generate_newsletter(today: str) -> str:
    """
    Generate the complete newsletter.

    Args:
        today:
            Date in YYYY-MM-DD format.

    Returns:
        Markdown newsletter content.
    """

    sections: List[Tuple[str, List[SummaryEntry]]] = []

    rendered_sections: List[str] = []

    for name, icon, feed_urls in SECTIONS:
        section_name, summaries = generate_section(
            f"{icon} {name}",
            feed_urls,
        )

        if summaries:
            sections.append(
                (
                    section_name,
                    summaries,
                )
            )

            rendered_sections.append(
                render(
                    section_name,
                    summaries,
                )
            )

    newsletter = "\n\n".join(
        [
            render_overview(
                today,
                sections,
            ),
            "\n\n".join(rendered_sections),
            quote_of_the_day(),
        ]
    )

    return newsletter

def generate_archive_page(
    archive_dir: Path,
) -> str:
    """
    Generate an archive page listing previous editions.
    """

    editions = sorted(
        archive_dir.glob("*.html"),
        reverse=True,
    )

    links = []

    for edition in editions:
        date = edition.stem

        links.append(
            f"""
            <li>
                <a href="archive/{edition.name}">
                    {date}
                </a>
            </li>
            """
        )

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Up Smyth Creek Archive</title>
<style>
body {{
    font-family: Arial, Helvetica, sans-serif;
    max-width: 800px;
    margin: 40px auto;
    padding: 20px;
    color: #111827;
}}

h1 {{
    font-size: 36px;
}}

a {{
    color: #2563eb;
    text-decoration: none;
}}

li {{
    margin: 12px 0;
    font-size: 18px;
}}
</style>
</head>

<body>

<h1>📚 Up Smyth Creek Archive</h1>

<p>
Previous editions of the newsletter.
</p>

<ul>
{"".join(links)}
</ul>

</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate the daily news summary newsletter."
    )

    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Generate newsletter without sending email.",
    )

    parser.add_argument(
        "--attach",
        action="store_true",
        help="Attach markdown file to email.",
    )

    args = parser.parse_args()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    output_dir = Path("output")
    output_dir.mkdir(
        exist_ok=True
    )

    logs_dir = Path("logs")
    logs_dir.mkdir(
        exist_ok=True
    )

    log_file = logs_dir / (
        f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )

    logger.info(
        "Starting newsletter generation"
    )

    try:
        newsletter = generate_newsletter(
            today
        )

        output_file = output_dir / (
            f"daily_{today}.md"
        )

        output_file.write_text(
            newsletter,
            encoding="utf-8",
        )

        logger.info(
            "Newsletter written to %s",
            output_file,
        )

        html_dir = Path("site")
        html_dir.mkdir(exist_ok=True)

        html_content = render_newsletter_html(
            newsletter
        )

        # Latest edition
        html_file = html_dir / "index.html"

        html_file.write_text(
            html_content,
            encoding="utf-8",
        )

        # Archive copy
        archive_dir = html_dir / "archive"
        archive_dir.mkdir(
            exist_ok=True
        )

        archive_file = archive_dir / f"{today}.html"

        archive_file.write_text(
            html_content,
            encoding="utf-8",
        )

        archive_page = html_dir / "archive.html"

        archive_page.write_text(
            generate_archive_page(
                archive_dir
            ),
            encoding="utf-8",
        )

        logger.info(
            "Archive page written to %s",
            archive_page,
        )

        logger.info(
            "HTML newsletter written to %s",
            html_file,
        )

        if (
            EMAIL_SEND_ENABLED
            and not args.no_email
        ):
            success = send_newsletter_email(
                newsletter,
                output_file if args.attach else None,
                subject=build_newsletter_title(today),
            )

            if success:
                logger.info(
                    "Newsletter emailed successfully"
                )
            else:
                logger.error(
                    "Newsletter generated but email failed"
                )

        elif args.no_email:
            logger.info(
                "Email skipped by user request"
            )

        else:
            logger.info(
                "Email disabled"
            )

        logger.info(
            "Newsletter generation complete"
        )

    except Exception:
        logger.error(
            "Fatal newsletter generation error",
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    main()