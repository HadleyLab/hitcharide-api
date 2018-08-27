from datetime import timedelta
from django.utils import timezone

from api.tests import APITestCase
from apps.accounts.factories import UserFactory

from apps.places.factories import CityFactory
from apps.rides.factories import CarFactory, RideFactory, RideBookingFactory
from apps.rides.models import Ride, Car


class RideViewSetTest(APITestCase):
    def setUp(self):
        super(RideViewSetTest, self).setUp()
        self.city1 = CityFactory.create()
        self.city2 = CityFactory.create()
        self.car = CarFactory.create(
            owner=self.user,
            brand='some',
            model='car',
            number_of_sits=5)

    def get_ride_data(self):
        now = timezone.now()
        return {
            'stops': [
                {'stop': self.city1.pk, 'cost_per_sit': 0, 'order': 1},
                {'stop': self.city2.pk, 'cost_per_sit': 100, 'order': 2},
            ],
            'start': now + timedelta(days=1),
            'end': now + timedelta(days=2),
            'number_of_sits': 5
        }

    def test_create_unauthorized_forbidden(self):
        data = self.get_ride_data()
        data.update({'car': {'pk': self.car.pk}})
        resp = self.client.post('/rides/ride/', data, format='json')
        self.assertUnauthorized(resp)

    def test_create_with_existing_car(self):
        self.authenticate()

        data = self.get_ride_data()
        data.update({'car': {'pk': self.car.pk}})
        resp = self.client.post('/rides/ride/', data, format='json')
        self.assertSuccessResponse(resp)

    def test_create_with_nested_car(self):
        self.authenticate()

        cars_count_before = Car.objects.all().count()
        data = self.get_ride_data()
        data.update({'car': {
            'brand': 'another',
            'model': 'car',
            'number_of_sits': 3,
        }})
        resp = self.client.post('/rides/ride/', data, format='json')
        self.assertSuccessResponse(resp)

        ride = Ride.objects.get(pk=resp.data['pk'])
        self.assertEqual(ride.stops.all().count(), 2)
        self.assertEqual(ride.car.brand, 'another')
        self.assertEqual(Car.objects.all().count(), cars_count_before + 1)

    def test_list_unauthorized(self):
        resp = self.client.get('/rides/ride/', format='json')
        self.assertUnauthorized(resp)

    def test_list(self):
        self.authenticate()

        car = CarFactory.create(owner=self.user)
        now = timezone.now()
        tomorrow = now - timedelta(days=1)
        yesterday = now + timedelta(days=1)

        RideFactory.create(
            start=tomorrow,
            end=yesterday,
            number_of_sits=5,
            car=car)
        ride = RideFactory.create(
            start=yesterday,
            end=yesterday,
            number_of_sits=5,
            car=car)

        resp = self.client.get('/rides/ride/', format='json')
        self.assertSuccessResponse(resp)

        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['pk'], ride.pk)

    def test_my_unauthorized(self):
        resp = self.client.get('/rides/ride/my/', format='json')
        self.assertUnauthorized(resp)

    def test_my(self):
        self.authenticate()

        car = CarFactory.create(owner=self.user)
        now = timezone.now()
        tomorrow = now - timedelta(days=1)
        yesterday = now + timedelta(days=1)

        my_ride_1 = RideFactory.create(
            start=tomorrow,
            end=yesterday,
            number_of_sits=5,
            car=car)
        my_ride_2 = RideFactory.create(
            start=yesterday,
            end=yesterday,
            number_of_sits=5,
            car=car)

        another_user = UserFactory.create()
        another_car = CarFactory.create(owner=another_user)
        RideFactory.create(
            start=tomorrow,
            end=yesterday,
            number_of_sits=5,
            car=another_car)

        resp = self.client.get('/rides/ride/my/', format='json')
        self.assertSuccessResponse(resp)
        self.assertListEqual(
            [my_ride_1.pk, my_ride_2.pk],
            [ride['pk'] for ride in resp.data])


class RideBookingViewSetTest(APITestCase):
    def setUp(self):
        super(RideBookingViewSetTest, self).setUp()
        self.city1 = CityFactory.create()
        self.city2 = CityFactory.create()

        self.car = CarFactory.create(
            owner=self.user,
            brand='some',
            model='car',
            number_of_sits=5)

        self.ride = RideFactory.create(car=self.car)
        self.booking = RideBookingFactory.create(
            ride=self.ride,
            client=self.user)

    def test_list_unauthorized(self):
        resp = self.client.get('/rides/booking/', format='json')
        self.assertForbidden(resp)

    def test_list(self):
        another_user = UserFactory.create()
        another_booking = RideBookingFactory.create(
            ride=self.ride,
            client=another_user)

        self.authenticate()
        resp = self.client.get('/rides/booking/', format='json')
        self.assertSuccessResponse(resp)
        self.assertListEqual([self.booking.pk],
                             [book['pk'] for book in resp.data])

        self.authenticate_as(another_user.username, another_user.password)
        resp = self.client.get('/rides/booking/', format='json')
        self.assertSuccessResponse(resp)
        self.assertListEqual([another_booking.pk],
                             [book['pk'] for book in resp.data])
