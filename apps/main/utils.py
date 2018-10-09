import os
import time
from dbmail import send_db_mail
from django.conf import settings


def send_mail(slug, recipient, context=None, *args, **kwargs):
    context = context or {}
    context.update({'frontend_url': settings.FRONTEND_URL,
                    'backend_url': settings.BACKEND_URL})
    send_db_mail(slug, recipient, context, *args, **kwargs)


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
