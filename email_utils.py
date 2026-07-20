import logging
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Union

import markdown

from config import *

logger = logging.getLogger(__name__)


def send_newsletter_email(
    newsletter_text: str,
    attachment_path: Optional[Union[Path, str]] = None,
    subject: Optional[str] = None,
) -> bool:
    """Send the generated newsletter by email.

    Args:
        newsletter_text: The body text of the newsletter.
        attachment_path: Optional markdown path to attach.
        subject: Optional email subject line.

    Returns:
        bool: True when email send succeeds, False otherwise.
    """
    if not EMAIL_SEND_ENABLED:
        logger.warning("Email sending is disabled because SMTP settings are incomplete.")
        return False

    message = EmailMessage()
    message["From"] = EMAIL_FROM or SMTP_USERNAME
    message["To"] = ", ".join(EMAIL_TO)
    message["Subject"] = subject or EMAIL_SUBJECT
    message.set_content(newsletter_text)

    html_body = markdown.markdown(
        newsletter_text,
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )
    message.add_alternative(html_body, subtype="html")

    if attachment_path:
        path = Path(attachment_path)
        if path.exists():
            message.add_attachment(
                path.read_bytes(),
                maintype="text",
                subtype="markdown",
                filename=path.name,
            )
        else:
            logger.warning(f"Attachment path does not exist: {path}")

    try:
        if EMAIL_USE_TLS:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(message)
        else:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as smtp:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(message)

        logger.info(f"Newsletter emailed to {EMAIL_TO}")
        return True
    except Exception as e:
        logger.error(f"Failed to send newsletter email: {e}", exc_info=True)
        return False
