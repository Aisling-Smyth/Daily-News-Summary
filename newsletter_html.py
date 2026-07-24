import html
import re
from datetime import datetime
import markdown

from config import NEWSLETTER_URL


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

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{safe_title}</title>
<style>
/* Reset styles for consistency across email clients */
body, table, td, a {{
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
}}
table, td {{
    mso-table-lspace: 0pt;
    mso-table-rspace: 0pt;
}}
img {{
    -ms-interpolation-mode: bicubic;
    border: 0;
    height: auto;
    line-height: 100%;
    outline: none;
    text-decoration: none;
}}
table {{
    border-collapse: collapse !important;
}}

body {{
    margin: 0 !important;
    padding: 0 !important;
    background-color: #ffffff !important;
    font-family: Arial, Helvetica, sans-serif;
    width: 100% !important;
}}

.email-wrapper {{
    width: 100% !important;
    background-color: #ffffff !important;
    margin: 0;
    padding: 0;
}}

.email-container {{
    width: 100% !important;
    max-width: 100% !important;
    background: #ffffff !important;
}}

.header-section {{
    background: #111827;
    padding: 50px 30px;
    color: white;
    text-align: center;
}}

.content-section {{
    padding: 40px 60px;
    color: #111827;
    font-size: 17px;
    line-height: 1.75;
}}

.section-title {{
    margin-top: 42px;
    margin-bottom: 24px;
}}

.section-title h2 {{
    font-size: 28px;
    font-weight: 700;
    border-bottom: 3px solid #111827;
    padding-bottom: 10px;
    margin: 0;
}}

.story-card {{
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}

.story-card h3 {{
    margin: 0 0 14px;
    font-size: 24px;
    line-height: 1.3;
    color: #111827;
}}

.story-card > p {{
    margin: 0 0 18px;
    font-size: 17px;
    line-height: 1.75;
    color: #374151;
}}

.story-card ul {{
    margin-top: 12px;
}}

.story-card li {{
    margin-bottom: 10px;
    line-height: 1.7;
}}

.read-button {{
    margin-top: 18px;
}}

.read-button a {{
    display: inline-block;
    background: #111827;
    color: #ffffff !important;
    text-decoration: none;
    padding: 12px 20px;
    border-radius: 999px;
    font-size: 15px;
    font-weight: 600;
}}

.footer-section {{
    background: #f9fafb;
    padding: 30px;
    text-align: center;
    font-size: 13px;
    color: #6b7280;
    border-top: 1px solid #e5e7eb;
}}

a {{
    color: #2563eb;
}}

h1 {{
    margin: 0;
}}

@media only screen and (max-width: 600px) {{
    .content-section {{
        padding: 25px 20px !important;
    }}
    .header-section {{
        padding: 40px 20px !important;
    }}
    .story-card {{
        padding: 18px;
    }}
    .section-title h2 {{
        font-size: 24px;
    }}
}}
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

{interactive_button}

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