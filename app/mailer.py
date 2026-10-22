import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import Config

# =========================
# Core Email Logic
# =========================


def send_email_with_attachment(
    subject: str, body: str, sender_email: str, receiver_email: str, password: str, file_path: str
) -> bool:
    """
    Sends an email with an attachment.
    If attachment exceeds max size, sends a download link instead.

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        DOWNLOAD_BASE_URL = Config.DOWNLOAD_BASE_URL
        max_attachment_size_mb = Config.MAX_ATTACHMENT_MB
        SMTP_SERVER = Config.SMTP_SERVER
        SMTP_PORT = Config.SMTP_PORT

        message.attach(MIMEText(body, "plain"))

        attachment_name = os.path.basename(file_path)
        file_size_bytes = os.path.getsize(file_path)

        if file_size_bytes > max_attachment_size_mb * 1024 * 1024:
            download_link = f"{DOWNLOAD_BASE_URL}/{attachment_name}"
            link_body = (
                f"\n\nAttachment exceeds {max_attachment_size_mb} MB.\n"
                f"Download it here:\n{download_link}"
            )
            message.attach(MIMEText(link_body, "plain"))
        else:
            with open(file_path, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())

            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{attachment_name}"')
            message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(sender_email, password)
            server.send_message(message)

        return True

    except Exception as exc:
        print(f"[Mailer Error] {exc}")
        return False


# =========================
# Public API (USED BY SCRAPER)
# =========================


def send_scrape_email(output_file: str) -> None:
    """
    Sends the scraping output via email.
    This is the ONLY function other modules should call.
    """

    sender_email = Config.sender_email
    receiver_email = Config.receiver_email
    password = Config.emaiL_password

    if not all([sender_email, receiver_email, password]):
        raise EnvironmentError(
            "Email credentials not set. "
            "Expected SCRAPER_EMAIL_SENDER, SCRAPER_EMAIL_RECEIVER, SCRAPER_EMAIL_PASSWORD"
        )

    subject = "Web Scraping Output File"
    body = (
        "The scraping process has completed successfully.\n\n"
        "Please find the output file attached or linked below."
    )

    success = send_email_with_attachment(
        subject=subject,
        body=body,
        sender_email=sender_email,
        receiver_email=receiver_email,
        password=password,
        file_path=output_file,
    )

    if not success:
        raise RuntimeError("Failed to send scraping email")
