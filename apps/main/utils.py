from dbmail import send_db_mail


def send_mail(slug, recipient, context=None, *args, **kwargs):
    context = context or {}
    context.update({'frontend_url': '',
                    back})
    send_db_mail(slug, recipient, context, *args, **kwargs)
