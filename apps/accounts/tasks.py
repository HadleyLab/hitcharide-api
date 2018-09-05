from django.conf import settings

from celery import shared_task
from twilio.rest import Client


client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)


@shared_task
def send_sms(phone, message):
    client.messages.create(body=message,
                           from_=settings.TWILIO_PHONE,
                           to=phone)
