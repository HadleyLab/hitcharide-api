from random import randint

from django.core.cache import cache
from django.conf import settings


def random_digit(len):
    range_start = 10**(len-1)
    range_end = (10**len)-1
    return randint(range_start, range_end)


def generate_sms_code():
    return str(random_digit(4))


def get_user_code_key(user_pk):
    return 'user_sms_code:{pk}'.format(pk=user_pk)


def save_user_code(user_pk, code):
    cache.set(get_user_code_key(user_pk), code, timeout=None)


def check_user_code(user_pk, code):
    return cache.get(get_user_code_key(user_pk)) == code


def check_twilio_enabled():
    return settings.TWILIO_SID and \
           settings.TWILIO_TOKEN and \
           settings.TWILIO_PHONE
