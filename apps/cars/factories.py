from factory import fuzzy
from factory.django import DjangoModelFactory

from apps.cars.models import Car


class CarFactory(DjangoModelFactory):
    brand = fuzzy.FuzzyText()
    model = fuzzy.FuzzyText()
    color = fuzzy.FuzzyText()
    license_plate = fuzzy.FuzzyText()
    number_of_seats = fuzzy.FuzzyInteger(low=2, high=7)

    class Meta:
        model = Car
