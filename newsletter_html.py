import html
import re
from datetime import datetime
import markdown

from config import NEWSLETTER_URL
from styles import load_styles


def extract_title(markdown_text: str) -> tuple[str, str]:
    """Extract newsletter title and date from markdown heading."""
    title = "Daily Brief"
    date = ""

    match = re.search(
        r"#\s+(.*?)$",
        markdown_text,
        re.MULTILINE,
    )

    if match:
        title_line = match.group(1)
        title = title_line

        date_match = re.search(
            r"(\d{1,2}\s+\w+\s+\d{4})",
            title_line,
        )

        if date_match:
            date = date_match.group(1)

    return title, date


def clean_markdown(markdown_text: str) -> str:
    """Remove markdown elements that don't render nicely in email."""
    cleaned = markdown_text
    cleaned = cleaned.replace("---", "")
    return cleaned


def add_story_cards(html_body: str) -> str:
    """Convert story headings into visual cards."""
    html_body = html_body.replace("<h2>", '<div class="section-title"><h2>')
    html_body = html_body.replace("</h2>", "</h2></div>")

    html_body = re.sub(
        r"<h3>(.*?)</h3>",
        r"""
<div class="story-card">
<h3>\1</h3>
""",
        html_body,
    )

    html_body = html_body.replace(
        "<p><a",
        """
<div class="read-button">
<p><a
""",
    )

    html_body = html_body.replace("</a></p>", "</a></p></div></div>")

    return html_body


def render_newsletter_html(
    newsletter_text: str,
) -> str:
    """Convert newsletter markdown into styled HTML email."""
    title, date = extract_title(newsletter_text)

    cleaned = clean_markdown(newsletter_text)

    body = markdown.markdown(
        cleaned,
        extensions=[
            "extra",
            "sane_lists",
        ],
        output_format="html5",
    )

    body = add_story_cards(body)

    safe_title = html.escape(title)

    interactive_button = f"""
    <a href="{NEWSLETTER_URL}" style="
        display:inline-block;
        background:#ffffff;
        color:#111827 !important;
        text-decoration:none;
        padding:12px 24px;
        border-radius:999px;
        font-size:15px;
        font-weight:700;
    ">
        🌐 Read the Interactive Edition
    </a>
    """

    archive_button = f"""
    <a href="{NEWSLETTER_URL}archive.html" style="
        display:inline-block;
        background:#ffffff;
        color:#111827 !important;
        text-decoration:none;
        padding:12px 24px;
        border-radius:999px;
        font-size:15px;
        font-weight:700;
    ">
        📚 Archive
    </a>
    """

    css = load_styles()

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{safe_title}</title>

<style>
{css}
</style>

</head>
<body>

<table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td align="center">

<table class="email-container" width="100%" cellpadding="0" cellspacing="0" border="0">

<!-- HEADER -->
<tr>
<td class="header-section">
<h1 style="font-size:42px; font-weight:700; margin:0;">
Up Smyth Creek
</h1>

<p style="margin:14px auto 24px; font-size:18px; line-height:1.5; opacity:.88; max-width:600px;">
When the world's up the creek, we'll help you paddle.
</p>

<div style="text-align:center;">
    {interactive_button}
    &nbsp;&nbsp;
    {archive_button}
</div>

</td>
</tr>

<!-- CONTENT -->
<tr>
<td class="content-section">
{body}
</td>
</tr>

<!-- FOOTER -->
<tr>
<td class="footer-section">
<p style="margin:0;">
That’s a wrap on today’s <strong>current</strong> news. Let's keep <strong>paddling</strong> along, and hope we don't land <strong>Up Smyth Creek</strong>!
</p>
</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""