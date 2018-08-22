from factory import DjangoModelFactory, fuzzy

from .models import Ride, Car


class CarFactory(DjangoModelFactory):
    brand = fuzzy.FuzzyText()
    model = fuzzy.FuzzyText()
    number_of_sits = fuzzy.FuzzyInteger(low=2, high=7)

    class Meta:
        model = Car


class RideFactory(DjangoModelFactory):

    class Meta:
        model = Ride
