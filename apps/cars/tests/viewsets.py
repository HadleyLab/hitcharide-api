from datetime import timedelta
from unittest import mock

from django.utils import timezone

from apps.main.test_utils import assert_mock_called_with
from config.tests import APITestCase
from apps.accounts.factories import UserFactory
from apps.places.factories import CityFactory
from apps.rides.factories import RideFactory, \
    RideBookingFactory, RideStopFactory, RideComplaintFactory, \
    RideRequestFactory
from apps.cars.factories import CarFactory
from apps.rides.models import Ride, RideComplaintStatus, RideStatus, \
    RideBookingStatus


class CarViewSetTest(APITestCase):
    def setUp(self):
        super(CarViewSetTest, self).setUp()
        self.city1 = CityFactory.create()
        self.city2 = CityFactory.create()
        self.car = CarFactory.create(
            owner=self.user,
            brand='some',
            model='car',
            number_of_seats=5)

    def test_delete_car_without_rides(self):
        self.authenticate()

        resp = self.client.delete('/rides/car/{0}/'.format(self.car.pk))
        self.assertSuccessResponse(resp)
        self.car.refresh_from_db()
        self.assertEqual(self.car.is_deleted, True)

    def test_delete_car_with_rides(self):
        self.authenticate()
        RideFactory.create(car=self.car)

        resp = self.client.delete('/rides/car/{0}/'.format(self.car.pk))
        self.assertForbidden(resp)
        self.car.refresh_from_db()
        self.assertEqual(self.car.is_deleted, False)
