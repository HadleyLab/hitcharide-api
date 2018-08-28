import string

from django.contrib.auth import get_user_model
from django.utils import timezone
from factory import DjangoModelFactory, fuzzy, \
    PostGenerationMethodCall, Sequence


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    phone = fuzzy.FuzzyText(length=10, chars=string.digits)
    first_name = fuzzy.FuzzyText()
    last_name = fuzzy.FuzzyText()
    birthday = fuzzy.FuzzyDateTime(start_dt=timezone.now().replace(year=1990))
    password = PostGenerationMethodCall('set_password', 'password')
    email = Sequence(lambda n: 'user{0}@example.com'.format(n))
