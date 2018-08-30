from random import randint

from django.core.cache import cache


def random_digit(len):
    range_start = 10**(len-1)
    range_end = (10**len)-1
    return randint(range_start, range_end)


def generate_and_send_sms_code(phone):
    return str(random_digit(4))


def get_user_code_key(user_pk):
    return 'user_sms_code:{pk}'.format(pk=user_pk)


def save_user_code(user_pk, code):
    cache.set(get_user_code_key(user_pk), code, timeout=None)


def check_user_code(user_pk, code):
    return cache.get(get_user_code_key(user_pk)) == code
