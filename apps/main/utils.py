import os
import time

from django.contrib.sites.models import Site
from django.conf import settings
from django.core.cache import cache
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


def get_twilio_proxy_session_key(source_phone, destination_phone):
    return 'twilio_proxy_session:{0}:{1}'.format(
        source_phone, destination_phone)


def get_twilio_proxy_sesssion_id(source_phone, destination_phone):
    return cache.get(
        get_twilio_proxy_session_key(source_phone, destination_phone))


def set_twilio_proxy_session_id(source_phone, destination_phone, session_id):
    # Set limit to one day just for keeping cache cleaned
    timeout = 24 * 60 * 60

    cache.set(
        get_twilio_proxy_session_key(source_phone, destination_phone),
        session_id, timeout=timeout)
    cache.set(
        get_twilio_proxy_session_key(destination_phone, source_phone),
        session_id, timeout=timeout)


def twilio_create_proxy_number(source_phone, destination_phone):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    service = client.proxy.services(
        settings.TWILIO_PASSENGER_AND_DRIVER_SESSION_ID)

    # Close previously created session (if not closed)
    # TODO: investigate how to increase ttl
    # for already existing session to avoid re-creating
    existing_session_id = get_twilio_proxy_sesssion_id(
        source_phone, destination_phone)
    if existing_session_id:
        try:
            session = service.sessions(existing_session_id).fetch()
            if session.status != session.Status.CLOSED:
                session.update(status=session.Status.CLOSED)
        except TwilioException:
            pass

    session = service.sessions.create(
        ttl=settings.TWILIO_PASSENGER_AND_DRIVER_SESSION_TTL)
    set_twilio_proxy_session_id(source_phone, destination_phone, session.sid)

    try:
        session.participants.create(identifier=destination_phone)
        return session.participants.create(
            identifier=source_phone).proxy_identifier
    except TwilioException:
        session.delete()
        return None
