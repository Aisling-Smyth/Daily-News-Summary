"""
Up Smyth Creek -- newsletter generator

Builds output.html from the CONTENT below, styled to match the pond
template. A few random critter illustrations from IMAGES_DIR are sprinkled
into fixed, reliably-visible spots (a card edge, a closing row) each run,
rather than floating freely across the whole page.
"""

import os
import random
from html import escape
from pathlib import Path
from config import NEWSLETTER_URL
from config import QUOTE_FEED_URL
import feedparser

# ---------------------------------------------------------------------------
# CONFIG -- adjust these for your machine/project
# ---------------------------------------------------------------------------
IMAGES_DIR = "images"   
LOGO_PATH = os.path.join(IMAGES_DIR, "logo.png")       # folder of decorative critter illustrations
OUTPUT_FILE = "output.html"

# ---------------------------------------------------------------------------
# Image discovery
# ---------------------------------------------------------------------------

def find_images(folder):
    exts = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
    base = Path(folder).resolve()

    return [
        p.as_uri()
        for p in base.rglob("*")
        if p.suffix.lower() in exts
        and "originals" not in (part.lower() for part in p.parts)
        and p.stem.lower() != "logo"
    ]


def resolve_asset(path_str):
    """Turn a path like 'images/logo.png' into an absolute file:// URI so it
    resolves correctly no matter which folder the final HTML is written to."""
    return Path(path_str).resolve().as_uri()


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------
def render_story(story, critter_image=None, side="left"):
    critter_html = ""
    if critter_image:
        top = random.randint(5, 75)
        rotation = random.randint(-15, 15)

        critter_html = (
            f'<img class="story-critter {side}" '
            f'src="{escape(critter_image, quote=True)}" alt="" '
            f'style="top:{top}%; transform:rotate({rotation}deg);">'
        )

    return f"""
        <article class="story">
          {critter_html}
          <div class="story-body">
            <h3>{escape(story.get('headline', 'Untitled'))}</h3>
            <p>{escape(story.get('summary', ''))}</p>
            <a class="story-link" href="{escape(story.get('link', '#'), quote=True)}" target="_blank" rel="noopener">
                Read more &rarr;
            </a>
          </div>
        </article>
    """


def _pop_random_image(available, all_images):
    """Pop one image from `available`, refilling + reshuffling from
    `all_images` whenever it runs out."""
    if not available:
        if not all_images:
            return None
        available.extend(all_images)
        random.shuffle(available)
    return available.pop() if available else None


def render_section(section, available, all_images):
    stories_html = "\n".join(
        render_story(
            s,
            critter_image=_pop_random_image(available, all_images),
            side="left" if i % 2 == 0 else "right",
        )
        for i, s in enumerate(section["stories"])
    )

    return f"""
    <section class="category-card" id="{section['id']}">
      <h2>{section['emoji']} {escape(section['name'])}</h2>
      <div class="stories">
        {stories_html}
      </div>
    </section>
    """


def render_sections(all_sections, images):
    available = images.copy()
    random.shuffle(available)

    parts = [
        render_section(section, available, images)
        for section in all_sections
    ]

    return "\n".join(parts)


def render_toc(all_sections):
    if not all_sections:
        return ""

    links = "\n".join(
        f'<a href="#{s["id"]}">{s["emoji"]} {escape(s["name"])}</a>'
        for s in all_sections
    )
    return f'<nav class="toc">{links}</nav>'

def render_email_summary(
    all_sections,
    newsletter_url,
):
    """
    Render a lightweight HTML email summary.

    The full illustrated newsletter lives on GitHub Pages.
    This email only provides headlines and a link.
    """

    section_html = []

    for section in all_sections:
        stories = "\n".join(
            f"""
            <li>
                {escape(story.get("headline", "Untitled"))}
            </li>
            """
            for story in section["stories"][:2]
        )

        section_html.append(
            f"""
            <h3>
                {section["emoji"]} {escape(section["name"])}
            </h3>

            <ul>
                {stories}
            </ul>
            """
        )

    return f"""
<!DOCTYPE html>
<html>
<body>

<div style="
    font-family: Arial, sans-serif;
    max-width:600px;
    margin:auto;
    color:#213452;
">

<h1 style="text-align:center;">
🌊 Up Smyth Creek
</h1>

<p style="text-align:center;">
<i>
When the world's up the creek, we'll help you paddle.
</i>
</p>


<div style="
    text-align:center;
    margin:30px 0;
">

<a href="{newsletter_url}"
style="
background:#365a7c;
color:white;
padding:14px 24px;
border-radius:20px;
text-decoration:none;
display:inline-block;
">

🐸 Open today's full edition

</a>

</div>


<h2>
Today's headlines
</h2>

{"".join(section_html)}


<hr>

<p style="
font-size:12px;
color:#666;
text-align:center;
">

The full illustrated edition is waiting for you 🌿

</p>


</div>

</body>
</html>
"""


"""
Quote retrieval for the newsletter.
"""

import logging
from html import escape

import feedparser

from config import QUOTE_FEED_URL

logger = logging.getLogger(__name__)


def quote_of_the_day() -> str:
    """
    Fetch and format the quote of the day.

    Returns:
        HTML for the quote section.
    """

    try:
        feed = feedparser.parse(QUOTE_FEED_URL)

        if not feed.entries:
            logger.warning("No quote found")
            return ""

        entry = feed.entries[0]

        author = getattr(entry, "title", "Unknown")
        quote = getattr(entry, "description", "")

        if not quote:
            return ""

        return quote, author

    except Exception:
        logger.exception("Failed to retrieve quote of the day")
        return ""

# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{safe_title}</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Short+Stack&display=swap" rel="stylesheet">

<style>
:root {
    --title-blue:   #213452;
    --heading-blue: #365a7c;
    --link-blue:    #5f7f9e;

    --card-bg: #fdfdf9;
    --page-bg: #dcebf1;
}

  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }

  body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    background: var(--page-bg);
    padding: 40px 16px;
    font-family: 'Short Stack', cursive;
  }

  .newsletter {
    position: relative;
    width: 100%;
    background:
      radial-gradient(circle at 18% 12%, rgba(255,255,255,0.55), transparent 40%),
      radial-gradient(circle at 82% 88%, rgba(255,255,255,0.4), transparent 45%),
      linear-gradient(165deg, #eef9fc 0%, #d7edf6 50%, #cfe7f3 100%);
    border-radius: 30px;
    box-shadow: 0 25px 50px rgba(35, 65, 85, 0.2);
    padding: 70px 70px 70px;
  }

  /* ---------- Header ---------- */
  .header {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 18px;
    padding-bottom: 6px;
    width: 100%;
  }

  .logo-hero {
    width: 150px;
    max-width: none;
    height: auto;
  }

  .title-block { text-align: center; }

  .title-block {
    text-align: center;
}

.title-block h1 {
    font-family: 'Baloo 2', cursive;
    font-weight: 800;
    color: var(--title-blue);
    font-size: 2.3rem;
    line-height: 1.05;
    margin: 0;
    letter-spacing: 0.5px;
}

.subtitle {
    font-family: 'Short Stack', cursive;
    color: var(--heading-blue);
    font-size: 0.9rem;
    margin: 8px 0 0;
    line-height: 1.4;
}

.overview-heading {
    font-family: 'Baloo 2', cursive;
    font-weight: 700;
    color: var(--title-blue);
    font-size: 1.3rem;
    text-align: left;
    margin: 22px 0 0;
    padding: 0 10px;
}

.intro-blurb {
    font-family: 'Short Stack', cursive;
    color: var(--title-blue);
    font-size: 0.98rem;
    line-height: 1.6;
    text-align: left;
    margin: 18px 0 0;
    padding: 0 10px;
}

.toc {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin: 18px 0 4px;
    padding: 0 10px;
}

.toc a {
    text-decoration: none;
    font-family: 'Short Stack', cursive;
    font-size: 0.85rem;
    color: var(--heading-blue);
    background: var(--page-bg);
    border: 1.5px solid var(--heading-blue);
    padding: 6px 14px;
    border-radius: 999px;
    white-space: nowrap;
}

.category-card h2 {
    font-family: 'Baloo 2', cursive;
    font-weight: 700;
    color: var(--title-blue);
    font-size: 1.25rem;
    margin: 0 0 16px;
}

.story-body h3 {
    font-family: 'Baloo 2', cursive;
    font-weight: 600;
    color: var(--heading-blue);
    font-size: 1.02rem;
    line-height: 1.3;
    margin: 0 0 4px;
}

.story-body p {
    font-family: 'Short Stack', cursive;
    color: #000;
    font-size: 0.95rem;
    line-height: 1.6;
    margin: 0 0 6px;
}

.story-body .story-link {
    font-family: 'Short Stack', cursive;
    font-size: 0.82rem;
    color: var(--link-blue);
    text-decoration: none;
    font-weight: 600;
}

.story-body .story-link:hover {
    color: var(--heading-blue);
}


/* ---------- Category cards ---------- */
.categories {
  display:flex;
  flex-direction:column;
  gap:24px;
  margin-top:28px;
}

.category-card{
  position:relative;
  background:var(--card-bg);
  border-radius:22px;
  padding:24px 26px;
  box-shadow:0 6px 16px rgba(60,95,75,0.08);
}

.stories{display:flex;flex-direction:column;gap:16px;}

.story{
  position:relative;
  padding-bottom:16px;
  border-bottom:1px dashed rgba(60,95,75,0.18);
}
.story:last-child{border-bottom:none;padding-bottom:0;}

.story-critter{
  position:absolute;
  width: auto;
  height:150px;
  object-fit:contain;
  pointer-events:none;
}
.story-critter.left{left:-130px;}
.story-critter.right{right:-150px;}

  /* ---------- Bottom row ---------- */
  .bottom-row {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 24px;
    margin-top: 28px;
  }
  .bottom-row img { width: 100px; height: auto; }

  .footer {
    text-align: center;
    margin-top: 22px;
    color: #000;
    font-family: 'Short Stack', cursive;
    font-size: 0.85rem;
    line-height: 1.6;
  }

  /* ---------- Responsive ---------- */
  @media (max-width: 620px) {
    .newsletter { padding: 30px 20px 36px; }
    .header { flex-direction: column; gap: 8px; }
    .logo-hero { width: 90px; }
    .title-block h1 { font-size: 1.8rem; }
    .story-critter { display: none; }
    .bottom-row { flex-wrap: wrap; gap: 14px; }
  }

.quote-footer{
    position:relative;
    width:900px;
    max-width:100%;
    margin:40px auto 20px;
}

.quote-scene{
    display:block;
    width:100%;
    height:auto;
}

.quote-content{
    position:absolute;
    left:49%;
    top:9%;
    width:43%;
    height:25%;

    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    gap: 4%; /* relative to container height, replaces margin-top on author */

    text-align:center;
    overflow:hidden;
}

.quote-content blockquote{
    margin:0;
    font-family:'Short Stack', cursive;
    font-size:2rem;
    line-height:1.15; /* was 1.3 — less leading top/bottom */
    font-style:italic;
    color:var(--heading-blue);
}

.quote-author{
    margin-top: 0;
    margin-bottom: -0.15em; /* pulls up to cancel reserved descender space */
    line-height: 1;
    font-family:'Baloo 2', cursive;
    font-size:1.4rem;
    font-weight:700;
    color:#222;
}

  /* ---------- Print ---------- */
  @media print {
    body { background: white; padding: 0; }
    .newsletter { box-shadow: none; max-width: 100%; }
  }
</style>
</head>
<body>

<div class="newsletter">

  <table class="header" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td width="25%" align="center">
        <img class="logo-hero" src="{logo_url}" alt="Logo">
      </td>

      <td width="75%" align="center">
        <div class="title-block">
          <h1>{safe_title}</h1>
          <p class="subtitle">When the world's up the creek, we'll help you paddle.</p>
        </div>
      </td>
    </tr>
  </table>

  <h2 class="overview-heading">{overview_heading}</h2>
  <p class="intro-blurb">{intro_blurb}</p>

  {toc_html}

  <div class="categories">
    {sections_html}
  </div>

<div class="quote-footer">

    <img
        src="{quote_scene}"
        class="quote-scene"
        alt=""
    >

    <div class="quote-content">

        <blockquote>
            {quote}
        </blockquote>
        <p class="quote-author">
            — {author}
        </p>

    </div>

</div>

<!-- FOOTER -->
  <table class="footer" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td class="footer-section" align="center">
<p style="margin:0; font-size:13px; color:#666;">
  That’s a wrap on today’s
  <b style="font-weight:900; color:var(--title-blue);">current</b>
  news. Let's keep
  <b style="font-weight:900; color:var(--title-blue);">paddling</b>
  along, and hope we don't land
  <b style="font-weight:900; color:var(--title-blue);">Up Smyth Creek</b>!
</p>

        <p style="margin:15px 0 0;">
          🛶 <a href="{NEWSLETTER_URL}archive.html" style="color: var(--heading-blue);"><b style="font-weight:900;">Float upstream</b> to past editions</a>
        </p>
      </td>
    </tr>
  </table>

</div>
<script>
function fitText(container) {
    const quote = container.querySelector("blockquote");
    const author = container.querySelector(".quote-author");
    const title = container.querySelector("h3");
    const els = [title, quote, author].filter(Boolean);

    const containerRect = container.getBoundingClientRect();

    function fits() {
        let top = Infinity, left = Infinity, right = -Infinity, bottom = -Infinity;
        els.forEach(el => {
            const r = el.getBoundingClientRect();
            top = Math.min(top, r.top);
            left = Math.min(left, r.left);
            right = Math.max(right, r.right);
            bottom = Math.max(bottom, r.bottom);
        });
        return (right - left) <= containerRect.width && (bottom - top) <= containerRect.height;
    }

    function applySize(size) {
        quote.style.fontSize = size + "px";
        author.style.fontSize = (size * 0.65) + "px";
        if (title) title.style.fontSize = (size * 0.8) + "px";
    }

    // Phase 1: shrink until it fits
    let size = 34;
    const minSize = 12;
    applySize(size);
    while (!fits() && size > minSize) {
        size -= 1;
        applySize(size);
    }

    // Phase 2: grow back up until it just stops fitting, then back off one step
    while (fits()) {
        size += 0.5;
        applySize(size);
    }
    size -= 0.5;
    applySize(size);
}
window.addEventListener("load", () => {
    document.querySelectorAll(".quote-content").forEach(fitText);
});
window.addEventListener("resize", () => {
    document.querySelectorAll(".quote-content").forEach(fitText);
});
</script>
</body>
</html>
"""