from factory import fuzzy, SubFactory
from factory.django import DjangoModelFactory

from apps.accounts.factories import UserFactory
from apps.cars.models import Car


class CarFactory(DjangoModelFactory):
    owner = SubFactory(UserFactory)
    brand = fuzzy.FuzzyText()
    model = fuzzy.FuzzyText()
    color = fuzzy.FuzzyText()
    license_plate = fuzzy.FuzzyText()
    number_of_seats = fuzzy.FuzzyInteger(low=2, high=7)

    class Meta:
        model = Car
