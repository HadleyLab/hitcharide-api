import re
from django.db import models


class PhoneField(models.CharField):
    max_len = 20

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = self.max_len
        super(PhoneField, self).__init__(*args, **kwargs)

    @staticmethod
    def get_normalized_phone(value):
        value = re.sub("[^0-9^.]", "", value)
        if len(value) < 6:
            return ''

        return value[:PhoneField.max_len]

    def get_prep_value(self, value):
        value = super(PhoneField, self).get_prep_value(value)
        if not value or not len(value):
            return value

        return self.get_normalized_phone(value)

    @staticmethod
    def get_printable(phone):
        if len(phone) == 11:
            return '+%s(%s%s%s)%s%s%s-%s%s%s%s' % tuple(phone)

        return phone
