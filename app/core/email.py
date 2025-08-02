# In app/core/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

# Get a logger instance for this module
logger = logging.getLogger(__name__)

def _send_email_sync(email_to: str, subject: str, html_content: str):
    """
    A robust, synchronous function to send an email using Python's smtplib.
    This is designed to be called from a synchronous environment like a Celery worker.
    """
    # Create the email message object
    msg = MIMEMultipart()
    msg['From'] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    try:
        # Connect to the SMTP server with a timeout to prevent hanging.
        with smtplib.SMTP(settings.MAIL_SERVER, 587, timeout=15) as server:
            server.starttls()  # Upgrade the connection to a secure (encrypted) one
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email sent successfully to {email_to}")
    except Exception as e:
        # Log any exceptions that occur during the email sending process.
        logger.error(f"Failed to send email to {email_to}: {e}", exc_info=True)
        # Re-raising the exception is important so Celery knows the task failed.
        raise

def send_verification_email_sync(email_to: str, token: str):
    """Builds and sends the verification email synchronously."""
    verification_url = f"http://localhost:8000/verify-email?token={token}"
    html_content = f"""
    <html>
    <body>
        <h1>Welcome to Bookly!</h1>
        <p>Thank you for signing up. Please click the link below to verify your account:</p>
        <a href="{verification_url}">Verify My Account</a>
        <p>This link will expire in 1 hour.</p>
    </body>
    </html>
    """
    _send_email_sync(email_to, "Verify Your Bookly Account", html_content)

def send_password_reset_email_sync(email_to: str, token: str):
    """Builds and sends the password reset email synchronously."""
    reset_url = f"http://localhost:8000/reset-password?token={token}"
    html_content = f"""
    <html>
    <body>
        <h1>Reset Your Password</h1>
        <p>You requested a password reset. Please click the link below to set a new password:</p>
        <a href="{reset_url}">Reset My Password</a>
        <p>This link will expire in 1 hour.</p>
    </body>
    </html>
    """
    _send_email_sync(email_to, "Reset Your Bookly Password", html_content)
