# News Summary

A small project that fetches RSS stories, clusters related headlines, summarizes them using an LLM, renders a markdown newsletter, and optionally emails the result.

## Quick start

1. Create and activate a virtualenv (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Create a .env file:

```bash
SMTP_SERVER=SMTP_SERVER
SMTP_PORT=SMTP_PORT
SMTP_USERNAME=SMTP_USERNAME
SMTP_PASSWORD=SMTP_PASSWORD
EMAIL_FROM=EMAIL_FROM
EMAIL_TO=EMAIL_TO
EMAIL_USE_TLS=true
```

If you use Gmail, prefer an app password (see Security → App passwords). If `EMAIL_SEND_ENABLED` is false the newsletter will still be generated locally but not emailed.

3. Run manually to test:

```bash
python3 main.py
# or without sending email
python3 main.py --no-email
# attach the generated markdown to the email
python3 main.py --attach
```

Output: `output/daily_<YYYY-MM-DD>.md` and logs in `logs/`.

## Troubleshooting

- If email is not sent, check `logs/newsletter_<date>.log` for reasons. Common causes:
  - SMTP credentials rejected (Gmail requires app passwords or OAuth)
  - Missing environment variables in the environment used by the scheduler

- To debug scheduler runs, inspect `logs/launchd_out.log` and `logs/launchd_err.log`.

## Security

- Do not commit `.env` or any secret values to version control.
- Prefer app-specific passwords where available.

## Files of interest

- `main.py` — orchestrates the pipeline
- `fetch.py`, `cluster.py`, `rank.py`, `summarise.py` — pipeline components
- `newsletter.py` — renders markdown output
- `email_utils.py` — sends email (converts markdown to HTML alternative)
- `run_newsletter.sh` — wrapper script used by `launchd`
