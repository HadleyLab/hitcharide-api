from factory import DjangoModelFactory, fuzzy

from .models import Ride, Car


class CarFactory(DjangoModelFactory):
    brand = fuzzy.FuzzyText()
    model = fuzzy.FuzzyText()

    class Meta:
        model = Car


class RideFactory(DjangoModelFactory):
    class Meta:
        model = Ride
