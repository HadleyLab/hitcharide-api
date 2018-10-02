from datetime import timedelta
from django.utils import timezone

from config.tests import APITestCase
from apps.places.factories import CityFactory
from apps.rides.factories import RideFactory, RideRequestFactory
from apps.cars.factories import CarFactory


class RideModelTest(APITestCase):
    def setUp(self):
        super(RideModelTest, self).setUp()
        self.city1 = CityFactory.create()
        self.city2 = CityFactory.create()
        self.city3 = CityFactory.create()
        self.city4 = CityFactory.create()
        self.car = CarFactory.create(
            owner=self.user,
            brand='some',
            model='car',
            number_of_seats=5)

    def test_get_ride_requests(self):
        now = timezone.now()
        tomorrow = now + timedelta(days=1)
        yesterday = now - timedelta(days=1)
        ride1 = RideFactory.create(
            car=self.car,
            city_from=self.city1,
            city_to=self.city2,
            date_time=tomorrow
        )
        ride2 = RideFactory.create(
            car=self.car,
            city_from=self.city2,
            city_to=self.city3,
            date_time=tomorrow
        )
        ride3 = RideFactory.create(
            car=self.car,
            city_from=self.city1,
            city_to=self.city3,
            stops_cities=[self.city4],
            date_time=tomorrow
        )
        request1 = RideRequestFactory.create(
            author=self.user,
            city_from=self.city1,
            city_to=self.city2,
            date_time=tomorrow
        )
        request2 = RideRequestFactory.create(
            author=self.user,
            city_from=self.city1,
            city_to=self.city4,
            date_time=tomorrow
        )
        request3 = RideRequestFactory.create(
            author=self.user,
            city_from=self.city1,
            city_to=self.city3,
            date_time=tomorrow
        )
        RideRequestFactory.create(
            author=self.user,
            city_from=self.city1,
            city_to=self.city2,
            date_time=yesterday
        )

        self.assertEqual(len(ride1.get_ride_requests()), 1)
        self.assertEqual(len(ride2.get_ride_requests()), 0)
        self.assertEqual(len(ride3.get_ride_requests()), 2)

        self.assertEqual(
            set(ride1.get_ride_requests().values_list('pk', flat=True)),
            {request1.pk})
        self.assertEqual(
            set(ride3.get_ride_requests().values_list('pk', flat=True)),
            {request2.pk, request3.pk})
