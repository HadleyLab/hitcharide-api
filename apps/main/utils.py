import os
import time

from decimal import Decimal
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from dbmail import send_db_mail, send_db_sms
from twilio.rest import Client, TwilioException


def get_context():
    current_site = Site.objects.get_current()

    return {
        'frontend_url': settings.FRONTEND_URL,
        'backend_url': settings.BACKEND_URL,
        'site_name': current_site.name,
    }


# TODO: create high-level wrapper which receives User as recipient
def send_mail(slug, recipient, context=None, *args, **kwargs):
    context = context or {}
    context.update(get_context())
    send_db_mail(slug, recipient, context, *args, **kwargs)


# TODO: create high-level wrapper which receives User as recipient
def send_sms(slug, recipient, context=None, *args, **kwargs):
    context = context or {}
    context.update(get_context())
    send_db_sms(slug, recipient, context, *args, **kwargs)


def round_decimal(num):
    # Rounds `num` to 2 digital places
    return num.quantize(Decimal('0.01'))


def get_timestamp():
    return int(time.time())


def generate_filename(source_filename, prefix=None):
    tstamp = get_timestamp()

    _, f_ext = os.path.splitext(source_filename)

    if prefix:
        return '{prefix}_{tstamp}{ext}'.format(
            prefix=prefix, tstamp=tstamp, ext=f_ext)
    else:
        return '{tstamp}{ext}'.format(
            prefix=prefix, tstamp=tstamp, ext=f_ext)


def to_iso(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_twilio_proxy_session_key(src_phone, dst_phone, context):
    return 'twilio_proxy_session:{0}:{1}:{2}'.format(
        src_phone, dst_phone, context)


def get_twilio_proxy_sesssion_id(src_phone, dst_phone, context):
    return cache.get(
        get_twilio_proxy_session_key(src_phone, dst_phone, context))


def set_twilio_proxy_session_id(src_phone, dst_phone, context,
                                session_id, date_expired):
    timeout = (date_expired - timezone.now()).seconds
    cache.set(
        get_twilio_proxy_session_key(src_phone, dst_phone, context),
        session_id, timeout=timeout)
    cache.set(
        get_twilio_proxy_session_key(dst_phone, src_phone, context),
        session_id, timeout=timeout)


def twilio_create_proxy_session(src_phone, dst_phone, context, date_expired):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    service = client.proxy.services(
        settings.TWILIO_PASSENGER_AND_DRIVER_SESSION_ID)

    # Try to get a previous opened session
    existing_session_id = get_twilio_proxy_sesssion_id(
        src_phone, dst_phone, context)
    if existing_session_id:
        try:
            session = service.sessions(existing_session_id).fetch()
            if session.status != session.Status.CLOSED:
                participants = session.participants.list()
                src_participant = [
                    p for p in participants if p.identifier == src_phone][0]
                dst_participant = [
                    p for p in participants if p.identifier == dst_phone][0]
                return session, src_participant, dst_participant
        except TwilioException:
            pass

    # Create a new session
    session = service.sessions.create(date_expiry=to_iso(date_expired))

    try:
        src_participant = session.participants.create(identifier=src_phone)
        dst_participant = session.participants.create(identifier=dst_phone)
        set_twilio_proxy_session_id(
            src_phone, dst_phone, context, session.sid, date_expired)
        return session, src_participant, dst_participant
    except TwilioException:
        session.delete()
        raise


def twilio_create_proxy_phone(src_phone, dst_phone, context, date_expired):
    session, src_participant, dst_participant = \
        twilio_create_proxy_session(
            src_phone, dst_phone, context, date_expired)
    return src_participant.proxy_identifier
