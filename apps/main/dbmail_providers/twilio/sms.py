from logging import getLogger

from django.conf import settings
from twilio.rest import Client

logger = getLogger()


def check_twilio_enabled():
    return settings.TWILIO_ACCOUNT_SID and \
           settings.TWILIO_AUTH_TOKEN and \
           settings.TWILIO_FROM


def send(sms_to, sms_body, **kwargs):
    if check_twilio_enabled():
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=sms_body,
            from_=settings.TWILIO_FROM,
            to=sms_to)
        return msg.account_sid
    else:
        logger.info('SMS {0}: {1}'.format(sms_to, sms_body))
