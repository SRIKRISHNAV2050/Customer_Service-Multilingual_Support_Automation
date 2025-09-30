"""
Notification wrappers:
- send_sms -> Twilio
- send_email -> SendGrid

Design:
- Keep these functions fast; use Celery to send in background to avoid blocking LLM flow.
- Add retry/backoff and error logging.
"""

from config import Config
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

_twilio_client = None
_sendgrid_client = None

def init_clients():
    global _twilio_client, _sendgrid_client
    if not _twilio_client and Config.TWILIO_ACCOUNT_SID:
        _twilio_client = TwilioClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    if not _sendgrid_client and Config.SENDGRID_API_KEY:
        _sendgrid_client = SendGridAPIClient(Config.SENDGRID_API_KEY)

def send_sms(to_number: str, body: str) -> dict:
    init_clients()
    msg = _twilio_client.messages.create(body=body, from_=Config.TWILIO_FROM_NUMBER, to=to_number)
    return {"sid": msg.sid, "status": msg.status}

def send_email(to_email: str, subject: str, html_body: str) -> dict:
    init_clients()
    mail = Mail(from_email=Config.SENDGRID_FROM_EMAIL, to_emails=to_email, subject=subject, html_content=html_body)
    resp = _sendgrid_client.send(mail)
    return {"status_code": resp.status_code}
