from django.utils import timezone

from factory import DjangoModelFactory, fuzzy, SubFactory

from .models import Ride, Car, RideBooking


class CarFactory(DjangoModelFactory):
    brand = fuzzy.FuzzyText()
    model = fuzzy.FuzzyText()
    number_of_sits = fuzzy.FuzzyInteger(low=2, high=7)

    class Meta:
        model = Car


class RideFactory(DjangoModelFactory):
    start = fuzzy.FuzzyDateTime(timezone.now())
    end = fuzzy.FuzzyDateTime(timezone.now())
    car = SubFactory(CarFactory)
    number_of_sits = fuzzy.FuzzyInteger(low=2, high=7)

    class Meta:
        model = Ride


class RideBookingFactory(DjangoModelFactory):
    ride = SubFactory(RideFactory)

    class Meta:
        model = RideBooking
