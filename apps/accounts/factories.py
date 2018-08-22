from django.contrib.auth import get_user_model
from factory import DjangoModelFactory, fuzzy, \
    PostGenerationMethodCall, Sequence


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = fuzzy.FuzzyText()
    age = fuzzy.FuzzyInteger(low=5, high=100)
    password = PostGenerationMethodCall('set_password', 'password')
    email = Sequence(lambda n: 'user{0}@example.com'.format(n))
