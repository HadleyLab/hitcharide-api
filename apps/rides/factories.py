from django.utils import timezone
from factory import DjangoModelFactory, fuzzy, SubFactory, Sequence

from apps.places.factories import CityFactory
from apps.accounts.factories import UserFactory
from .models import Ride, Car, RideBooking, RideStop, RideComplaint, \
    RideComplaintStatus


class CarFactory(DjangoModelFactory):
    brand = fuzzy.FuzzyText()
    model = fuzzy.FuzzyText()
    color = fuzzy.FuzzyText()
    license_plate = fuzzy.FuzzyText()
    number_of_seats = fuzzy.FuzzyInteger(low=2, high=7)

    class Meta:
        model = Car


class RideFactory(DjangoModelFactory):
    car = SubFactory(CarFactory)
    city_from = SubFactory(CityFactory)
    city_to = SubFactory(CityFactory)
    number_of_seats = fuzzy.FuzzyInteger(low=2, high=7)
    price = fuzzy.FuzzyInteger(low=2, high=100)
    date_time = fuzzy.FuzzyDateTime(start_dt=timezone.now().replace(year=2003))
    description = fuzzy.FuzzyText()

    class Meta:
        model = Ride


class RideStopFactory(DjangoModelFactory):
    ride = SubFactory(RideFactory)
    city = SubFactory(CityFactory)
    order = Sequence(lambda n: n)

    class Meta:
        model = RideStop


class RideBookingFactory(DjangoModelFactory):
    ride = SubFactory(RideFactory)

    class Meta:
        model = RideBooking


class RideComplaintFactory(DjangoModelFactory):
    ride = SubFactory(RideFactory)
    user = SubFactory(UserFactory)
    status = RideComplaintStatus.NEW
    description = fuzzy.FuzzyText()

    class Meta:
        model = RideComplaint
