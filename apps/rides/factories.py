from django.utils import timezone
from factory import DjangoModelFactory, fuzzy, SubFactory, Sequence

from apps.places.factories import CityFactory
from .models import Ride, Car, RideBooking, RidePoint


class CarFactory(DjangoModelFactory):
    brand = fuzzy.FuzzyText()
    model = fuzzy.FuzzyText()
    number_of_sits = fuzzy.FuzzyInteger(low=2, high=7)

    class Meta:
        model = Car


class RideFactory(DjangoModelFactory):
    car = SubFactory(CarFactory)
    number_of_sits = fuzzy.FuzzyInteger(low=2, high=7)

    class Meta:
        model = Ride


class RidePointFactory(DjangoModelFactory):
    ride = SubFactory(RideFactory)
    city = SubFactory(CityFactory)
    cost_per_sit = fuzzy.FuzzyInteger(low=2, high=100)
    order = Sequence(lambda n: n)
    date_time = fuzzy.FuzzyDateTime(start_dt=timezone.now().replace(year=2003))

    class Meta:
        model = RidePoint


class RideBookingFactory(DjangoModelFactory):
    ride = SubFactory(RideFactory)

    class Meta:
        model = RideBooking
