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
    generate_intro_blurb,
)
from html import escape
from styles import load_styles

from cluster import cluster
from rank import rank
from summarise import summarise

from on_this_day import get_on_this_day_card, get_fun_days_card

from config import NEWSLETTER_URL

from newsletter_html import (
    HTML_TEMPLATE,
    find_images,
    render_sections,
    render_toc,
    render_email_summary,
    resolve_asset,
    quote_of_the_day,
    resolve_asset,
)

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

def generate_sections():
    """
    Fetch and summarise stories.
    Returns sections data for rendering.
    """

    sections = []
    raw_sections = []

    for name, icon, feed_urls in SECTIONS:
        section_name, summaries = generate_section(
            f"{icon} {name}",
            feed_urls,
        )

        from slugify import slugify

        if summaries:
            raw_sections.append(
                (section_name, summaries)
            )

            sections.append(
                {
                    "id": slugify(name),
                    "emoji": icon,
                    "name": name,
                    "stories": summaries,
                }
            )

    return sections, raw_sections

def render_full_newsletter(today: str, sections, raw_sections) -> str:
    """
    Generate the complete HTML newsletter.

    Args:
        today:
            Date in YYYY-MM-DD format.

    Returns:
        HTML newsletter content.
    """

    story_images = [resolve_asset(p) for p in find_images("images")]

    if raw_sections:
        intro_blurb = generate_intro_blurb(today, raw_sections)
    else:
        intro_blurb = "No news to report today -- check back tomorrow!"
        
    toc_html = render_toc(sections)

    if not toc_html:
        logger.warning(
            "toc_html came back empty (sections had %d entries) -- "
            "the TOC nav will not appear in the output",
            len(sections),
        )

    sections_html = render_sections(
        sections,
        story_images,  # floating critters
    )

    on_this_day = get_on_this_day_card()

    if on_this_day:
        on_this_day_html = "".join(
            f"<p>• {escape(item)}</p>"
            for item in get_on_this_day_card()
        )

    quote, author = quote_of_the_day()

    fun_day = get_fun_days_card()

    if fun_day:
        fun_day_html = "".join(
            f"<p>• {escape(item)}</p>"
            for item in get_fun_days_card()
        )

    title = "Up Smyth Creek"
    html = HTML_TEMPLATE

    html = (html
        .replace("{safe_title}", escape(title))
        .replace("{overview_heading}", escape(f"Daily News Summary: {today}"))
        .replace("{logo_url}", resolve_asset("images/logo.png"))
        .replace("{intro_blurb}", escape(intro_blurb))
        .replace("{toc_html}", toc_html)
        .replace("{sections_html}", sections_html)
        .replace("{NEWSLETTER_URL}", NEWSLETTER_URL)
        .replace("{on_this_day_html}", on_this_day_html)
        .replace("{quote}", quote)
        .replace("{author}", author)
        .replace("{quote_scene}", resolve_asset("images/quote_otter.png"))
        .replace("{fun_day_html}", fun_day_html)
    )


    return html

def generate_archive_page(
    archive_dir: Path,
) -> str:
    """
    Generate a styled archive page listing previous editions.
    """

    # TODO: make it not ugly
    # TODO: "← Back to today's edition"

    editions = sorted(
        archive_dir.glob("*.html"),
        reverse=True,
    )

    cards = []

    for edition in editions:
        date = edition.stem

        try:
            formatted_date = datetime.strptime(
                date,
                "%Y-%m-%d",
            ).strftime(
                "%A, %d %B %Y"
            )
        except ValueError:
            formatted_date = date

        cards.append(
            f"""
<div class="archive-card">
    <h2>
        📖 {formatted_date}
    </h2>

    <p>
        Catch up on the latest edition of Up Smyth Creek.
    </p>

    <a href="archive/{edition.name}">
        Read edition →
    </a>
</div>
"""
        )

        css = load_styles()

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Up Smyth Creek Archive</title>

<style>
{css}
</style>

</head>

<body>

<div class="header">

<h1>
Up Smyth Creek
</h1>

<p>
📚 Previous editions of your daily news paddle.
</p>

</div>


<div class="container">

<h2 class="title">
Archive
</h2>

{"".join(cards)}

</div>


<div class="footer">
Thanks for reading <strong>Up Smyth Creek</strong>.
</div>

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
        sections, raw_sections = generate_sections()

        # TODO: create HTMLs of past versions
        full_html = render_full_newsletter(
            today, sections, raw_sections
        )

        # email_html = render_email_summary(
        #     sections,
        #     NEWSLETTER_URL,
        # )

        output_file = output_dir / (
            f"daily_{today}.html"
        )

        output_file.write_text(
            full_html,
            encoding="utf-8",
        )

        logger.info(
            "Newsletter written to %s",
            output_file,
        )

        # html_dir = Path("site")
        # html_dir.mkdir(exist_ok=True)

        # # Latest edition
        # html_file = html_dir / "index.html"

        # html_file.write_text(
        #     full_html,
        #     encoding="utf-8",
        # )

        # # Archive copy
        # archive_dir = html_dir / "archive"
        # archive_dir.mkdir(
        #     exist_ok=True
        # )

        # archive_file = archive_dir / f"{today}.html"

        # archive_file.write_text(
        #     full_html,
        #     encoding="utf-8",
        # )

        # archive_page = html_dir / "archive.html"

        # archive_page.write_text(
        #     generate_archive_page(
        #         archive_dir
        #     ),
        #     encoding="utf-8",
        # )

        # logger.info(
        #     "Archive page written to %s",
        #     archive_page,
        # )

        # logger.info(
        #     "HTML newsletter written to %s",
        #     html_file,
        # )

        # if (
        #     EMAIL_SEND_ENABLED
        #     and not args.no_email
        # ):
        #     success = send_newsletter_email(
        #         email_html,
        #         subject=build_newsletter_title(today),
        #     )

        #     if success:
        #         logger.info(
        #             "Newsletter emailed successfully"
        #         )
        #     else:
        #         logger.error(
        #             "Newsletter generated but email failed"
        #         )

        # elif args.no_email:
        #     logger.info(
        #         "Email skipped by user request"
        #     )

        # else:
        #     logger.info(
        #         "Email disabled"
        #     )

        # logger.info(
        #     "Newsletter generation complete"
        # )

    except Exception:
        logger.error(
            "Fatal newsletter generation error",
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    main()