import markdown
import html
import re
from datetime import datetime


def extract_title(markdown_text: str) -> tuple[str, str]:
    """
    Extract newsletter title and date from markdown heading.
    """

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
    """
    Remove markdown elements that don't render nicely in email.
    """

    cleaned = markdown_text
    cleaned = cleaned.replace("---", "")
    return cleaned


def add_story_cards(html_body: str) -> str:
    """
    Convert story headings into visual cards.
    """

    html_body = html_body.replace(
        "<h2>",
        '<div class="section-title"><h2>'
    )

    html_body = html_body.replace(
        "</h2>",
        "</h2></div>"
    )

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
"""
    )

    html_body = html_body.replace(
        "</a></p>",
        "</a></p></div></div>"
    )

    return html_body


def render_newsletter_html(
    newsletter_text: str,
) -> str:
    """
    Convert newsletter markdown into styled HTML email.
    """

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

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width, initial-scale=1.0">

<title>{safe_title}</title>

<style>

body {{
    margin:0;
    padding:0;
    background:#f3f4f6;
    font-family:Arial, Helvetica, sans-serif;
}}

.section-title {{
    margin-top:42px;
    margin-bottom:24px;
}}

.section-title h2 {{
    font-size:28px;
    font-weight:700;
    border-bottom:3px solid #111827;
    padding-bottom:10px;
    margin:0;
}}

.story-card {{
    background:#ffffff;
    border:1px solid #e5e7eb;
    border-radius:18px;
    padding:24px 28px;
    margin-bottom:24px;
    box-shadow:0 3px 10px rgba(0,0,0,0.06);
}}

.story-card h3 {{
    margin:0 0 14px;
    font-size:24px;
    line-height:1.3;
    color:#111827;
}}

.story-card > p {{
    margin:0 0 18px;
    font-size:17px;
    line-height:1.75;
    color:#374151;
}}

.story-card ul {{
    margin-top:12px;
}}

.story-card li {{
    margin-bottom:10px;
    line-height:1.7;
}}

.read-button {{
    margin-top:18px;
}}

.read-button a {{
    display:inline-block;
    background:#111827;
    color:#ffffff !important;
    text-decoration:none;
    padding:12px 20px;
    border-radius:999px;
    font-size:15px;
    font-weight:600;
}}

a {{
    color:#2563eb;
}}

h1 {{
    margin:0;
}}

@media only screen and (max-width:900px) {{

.story-card {{
    padding:18px;
}}

.section-title h2 {{
    font-size:24px;
}}

}}

</style>

</head>

<body>

<table
width="100%"
cellpadding="0"
cellspacing="0"
border="0"
style="
background:#f3f4f6;
padding:32px 0;
">

<tr>

<td align="center">

<table
width="900"
cellpadding="0"
cellspacing="0"
border="0"
style="
width:900px;
max-width:900px;
background:#ffffff;
border-radius:18px;
overflow:hidden;
">

<!-- HEADER -->

<tr>

<td
align="center"
style="
background:#111827;
padding:54px 50px;
color:white;
">

<h1
style="
font-size:60px;
font-weight:700;
margin:0;
">

Up Smyth Creek

</h1>

<p
style="
margin:18px auto 0;
font-size:22px;
line-height:1.5;
opacity:.88;
max-width:700px;
">

When the world's up the creek, we'll help you paddle.

</p>

<p
style="
margin:26px 0 0;
font-size:16px;
opacity:.7;
">

{html.escape(date)}

</p>

</td>

</tr>

<!-- CONTENT -->

<tr>

<td
style="
padding:40px 48px;
color:#111827;
font-size:17px;
line-height:1.75;
">

{body}</td>

</tr>

<!-- FOOTER -->

<tr>

<td
align="center"
style="
background:#f9fafb;
padding:30px;
font-size:13px;
color:#6b7280;
border-top:1px solid #e5e7eb;
">

<p style="margin:0;">
Thanks for reading <strong>Up Smyth Creek</strong>.
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