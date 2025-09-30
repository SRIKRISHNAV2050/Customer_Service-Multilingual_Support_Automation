"""
Background tasks to offload heavy or delayed work:
- Sending SMS / Email
- Creating CRM tickets
- Periodic analytics and retraining jobs
"""

from extensions import celery
from services.notifications import send_sms, send_email
from services.crm_service import create_crm_ticket

@celery.task(bind=True, max_retries=3)
def send_sms_task(self, to_number, body):
    try:
        return send_sms(to_number, body)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)

@celery.task(bind=True)
def create_ticket_task(self, conversation_id, summary, metadata=None):
    # call CRM and persist mapping in DB if required
    return create_crm_ticket(conversation_id, summary, metadata)
