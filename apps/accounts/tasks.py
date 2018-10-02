from django.conf import settings

from celery import shared_task
from twilio.rest import Client

from apps.accounts.utils import check_twilio_enabled


@shared_task
def send_sms(phone, message):
    if check_twilio_enabled():
        client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        client.messages.create(body=message,
                               from_=settings.TWILIO_PHONE,
                               to=phone)
    else:
        print(message)
