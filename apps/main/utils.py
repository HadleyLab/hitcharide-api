from dbmail import send_db_mail
from django.conf import settings


def send_mail(slug, recipient, context=None, *args, **kwargs):
    context = context or {}
    context.update({'frontend_url': settings.FRONTEND_URL,
                    'backend_url': settings.BACKEND_URL})
    send_db_mail(slug, recipient, context, *args, **kwargs)
