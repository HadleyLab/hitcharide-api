import os
import time

from django.contrib.sites.models import Site
from django.conf import settings

from dbmail import send_db_mail, send_db_sms


def get_context():
    current_site = Site.objects.get_current()

    return {
        'frontend_url': settings.FRONTEND_URL,
        'backend_url': settings.BACKEND_URL,
        'site_name': current_site.name,
    }


def send_mail(slug, recipient, context=None, *args, **kwargs):
    context = context or {}
    context.update(get_context())
    send_db_mail(slug, recipient, context, *args, **kwargs)


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
