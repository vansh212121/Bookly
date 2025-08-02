# In app/core/celery_tasks.py
import logging
from app.celery_app import celery_app
from app.core import email

# Get a logger for this module
logger = logging.getLogger(__name__)

@celery_app.task
def send_verification_email_task(email_to: str, token: str):
    """
    A Celery task that calls the synchronous email function for verification.
    """
    logger.info(f"Worker received task: send verification email to {email_to}")
    try:
        # We call our simple, synchronous email function. No async bridges needed.
        email.send_verification_email_sync(email_to=email_to, token=token)
        logger.info(f"Successfully sent verification email to {email_to}")
    except Exception as e:
        # If any error occurs, log it with details.
        logger.error(f"Failed to send verification email to {email_to}: {e}", exc_info=True)

@celery_app.task
def send_password_reset_email_task(email_to: str, token: str):
    """
    A Celery task that calls the synchronous email function for password resets.
    """
    logger.info(f"Worker received task: send password reset email to {email_to}")
    try:
        email.send_password_reset_email_sync(email_to=email_to, token=token)
        logger.info(f"Successfully sent password reset email to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email_to}: {e}", exc_info=True)
