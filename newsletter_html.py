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

    cleaned = cleaned.replace(
        "---",
        "",
    )

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
    Convert newsletter markdown into styled email HTML.

    Args:
        newsletter_text:
            Markdown newsletter.

    Returns:
        Complete HTML email.
    """

    title, date = extract_title(
        newsletter_text
    )

    cleaned = clean_markdown(
        newsletter_text
    )

    body = markdown.markdown(
        cleaned,
        extensions=[
            "extra",
            "sane_lists",
        ],
        output_format="html5",
    )

    body = add_story_cards(
        body
    )

    safe_title = html.escape(
        title
    )

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>
{safe_title}
</title>


<style>

.section-title {{
    margin-top:40px;
    margin-bottom:20px;
}}

.section-title h2 {{
    font-size:24px;
    border-bottom:3px solid #111827;
    padding-bottom:8px;
}}

.story-card {{
    background:#ffffff;
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:24px;
    margin-bottom:22px;
    box-shadow:0 2px 8px rgba(0,0,0,0.05);
}}

.story-card h3 {{
    font-size:21px;
    line-height:1.3;
    margin-top:0;
    margin-bottom:14px;
}}

.story-card p {{
    color:#374151;
    line-height:1.6;
}}

.read-button a {{
    display:inline-block;
    margin-top:12px;
    padding:10px 18px;
    background:#111827;
    color:white !important;
    border-radius:20px;
    font-size:14px;
    text-decoration:none;
}}

</style>


</head>


<body style="
margin:0;
padding:0;
background:#f4f5f7;
font-family:
Arial,
Helvetica,
sans-serif;
">


<table width="100%"
cellpadding="0"
cellspacing="0"
style="
background:#f4f5f7;
padding:30px 0;
">

<tr>

<td align="center"
style="
padding:0 15px;
">

<!-- RESPONSIVE WRAPPER -->

<table width="680"
cellpadding="0"
cellspacing="0"
style="
width:100%;
max-width:680px;
background:white;
border-radius:16px;
overflow:hidden;
">


<!-- HEADER -->

<tr>

<td style="
background:#111827;
padding:40px;
text-align:center;
color:white;
">


<h1 style="
margin:0;
font-size:36px;
font-weight:700;
">

Up Smyth Creek

</h1>


<p style="
margin:12px 0 0;
font-size:16px;
opacity:0.85;
">

When the world's up the creek, we'll help you paddle.

</p>


<p style="
margin:18px 0 0;
font-size:14px;
opacity:0.7;
">

{html.escape(date)}

</p>


</td>

</tr>



<!-- CONTENT -->

<tr>

<td style="
padding:40px;
color:#111827;
">


{body}


</td>

</tr>



<!-- FOOTER -->

<tr>

<td style="
background:#f9fafb;
padding:25px 40px;
text-align:center;
font-size:12px;
color:#6b7280;
">


</td>

</tr>


</table>

</td>

</tr>

</table>


</body>

</html>
"""