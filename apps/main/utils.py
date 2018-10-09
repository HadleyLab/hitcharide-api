import os
import time

from django.contrib.sites.models import Site
from django.conf import settings

from dbmail import send_db_mail


def send_mail(slug, recipient, context=None, *args, **kwargs):
    context = context or {}
    current_site = Site.objects.get_current()
    context.update({'frontend_url': settings.FRONTEND_URL,
                    'backend_url': settings.BACKEND_URL,
                    'site_name': current_site.name})
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
