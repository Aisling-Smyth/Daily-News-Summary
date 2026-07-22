import logging
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Union

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
from newsletter_html import render_newsletter_html


logger = logging.getLogger(__name__)


def send_newsletter_email(
    newsletter_text: str,
    attachment_path: Optional[
        Union[Path, str]
    ] = None,
    subject: Optional[str] = None,
) -> bool:
    """
    Send newsletter by email.

    Args:
        newsletter_text:
            Newsletter markdown content.

        attachment_path:
            Optional markdown attachment.

        subject:
            Optional email subject override.

    Returns:
        True if email sends successfully.
    """

    if not EMAIL_SEND_ENABLED:
        logger.warning(
            "Email sending disabled: "
            "SMTP settings incomplete"
        )
        return False

    message = EmailMessage()

    message["From"] = (
        EMAIL_FROM
        or SMTP_USERNAME
    )

    message["To"] = ", ".join(
        EMAIL_TO
    )

    message["Subject"] = (
        subject
        or EMAIL_SUBJECT
    )

    message.set_content(
        newsletter_text
    )

    html_body = render_newsletter_html(newsletter_text)

    message.add_alternative(
        html_body,
        subtype="html",
    )

    if attachment_path:
        attach_file(
            message,
            attachment_path,
        )

    try:
        if EMAIL_USE_TLS:
            send_tls_email(
                message
            )
        else:
            send_ssl_email(
                message
            )

        logger.info(
            "Newsletter email sent successfully"
        )

        return True

    except Exception:
        logger.error(
            "Failed to send newsletter email",
            exc_info=True,
        )

        return False


def attach_file(
    message: EmailMessage,
    attachment_path: Union[Path, str],
) -> None:
    """
    Attach markdown file if available.
    """

    path = Path(
        attachment_path
    )

    if not path.exists():
        logger.warning(
            "Attachment not found: %s",
            path,
        )
        return

    message.add_attachment(
        path.read_bytes(),
        maintype="text",
        subtype="markdown",
        filename=path.name,
    )


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

        smtp.send_message(
            message
        )


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

        smtp.send_message(
            message
        )