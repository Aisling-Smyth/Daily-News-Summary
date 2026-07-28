import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

from config import (
    EMAIL_FROM,
    EMAIL_SUBJECT,
    EMAIL_TO,
    EMAIL_SEND_ENABLED,
    EMAIL_USE_TLS,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
    SMTP_USERNAME,
)

logger = logging.getLogger(__name__)


def send_newsletter_email(
    newsletter_html: str,
    subject: Optional[str] = None,
) -> bool:
    """
    Send the newsletter as an HTML email.

    Args:
        newsletter_html:
            Rendered HTML newsletter.

        subject:
            Optional email subject override.

    Returns:
        True if the email was sent successfully.
    """

    if not EMAIL_SEND_ENABLED:
        logger.warning(
            "Email sending disabled: SMTP settings incomplete."
        )
        return False

    message = EmailMessage()

    message["From"] = EMAIL_FROM or SMTP_USERNAME
    message["To"] = ", ".join(EMAIL_TO)
    message["Subject"] = subject or EMAIL_SUBJECT

    # Plain text fallback for email clients that don't support HTML.
    message.set_content(
        "Your email client doesn't support HTML.\n\n"
        "Please view this newsletter in an HTML-capable email client."
    )

    # HTML body.
    message.add_alternative(
        newsletter_html,
        subtype="html",
    )

    try:
        if EMAIL_USE_TLS:
            send_tls_email(message)
        else:
            send_ssl_email(message)

        logger.info("Newsletter email sent successfully.")
        return True

    except Exception:
        logger.exception("Failed to send newsletter email.")
        return False


def send_tls_email(
    message: EmailMessage,
) -> None:
    """
    Send email using STARTTLS.
    """

    with smtplib.SMTP(
        SMTP_SERVER,
        SMTP_PORT,
        timeout=30,
    ) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(
            SMTP_USERNAME,
            SMTP_PASSWORD,
        )

        smtp.send_message(message)


def send_ssl_email(
    message: EmailMessage,
) -> None:
    """
    Send email using SSL.
    """

    with smtplib.SMTP_SSL(
        SMTP_SERVER,
        SMTP_PORT,
        timeout=30,
    ) as smtp:
        smtp.login(
            SMTP_USERNAME,
            SMTP_PASSWORD,
        )

        smtp.send_message(message)