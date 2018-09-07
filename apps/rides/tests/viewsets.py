from datetime import timedelta
from django.utils import timezone

from config.tests import APITestCase
from apps.accounts.factories import UserFactory
from apps.places.factories import CityFactory
from apps.rides.factories import CarFactory, RideFactory, \
    RideBookingFactory, RideStopFactory, RideComplaintFactory
from apps.rides.models import Ride, Car, RideComplaintStatus


class RideViewSetTest(APITestCase):
    def setUp(self):
        super(RideViewSetTest, self).setUp()
        self.city1 = CityFactory.create()
        self.city2 = CityFactory.create()
        self.car = CarFactory.create(
            owner=self.user,
            brand='some',
            model='car',
            number_of_seats=5)

    def get_ride_data(self):
        return {
            'city_from': self.city1.pk,
            'city_to': self.city2.pk,
            'price': 200,
            'date_time': timezone.now() + timedelta(days=1),
            'stops': [],
            'number_of_seats': 5
        }

    def test_create_unauthorized_forbidden(self):
        data = self.get_ride_data()
        data.update({'car': self.car.pk})
        resp = self.client.post('/rides/ride/', data, format='json')
        self.assertUnauthorized(resp)

    def test_create_with_existing_car(self):
        self.authenticate()

        data = self.get_ride_data()
        data.update({'car': self.car.pk})
        resp = self.client.post('/rides/ride/', data, format='json')
        self.assertSuccessResponse(resp)
        ride = Ride.objects.get(pk=resp.data['pk'])
        self.assertEqual(ride.stops.all().count(), 0)
        self.assertEqual(ride.car.brand, 'some')
        self.assertEqual(ride.car.owner.pk, self.user.pk)

    def test_create_with_unfilled_user(self):
        self.user.phone = None
        self.user.save()
        self.authenticate()

        data = self.get_ride_data()
        data.update({'car': self.car.pk})
        resp = self.client.post('/rides/ride/', data, format='json')
        self.assertBadRequest(resp)

    def test_update(self):
        self.authenticate()
        data = self.get_ride_data()
        data.update({'car': self.car.pk})
        resp = self.client.post('/rides/ride/', data, format='json')
        self.assertSuccessResponse(resp)

        ride_pk = resp.data['pk']

        city3 = CityFactory.create()
        data['stops'].append({
            'city': city3.pk,
            'order': 1,
        })
        resp = self.client.put('/rides/ride/{0}/'.format(ride_pk), data,
                               format='json')
        self.assertSuccessResponse(resp)
        self.assertEqual(len(resp.data['stops']), 1)
        self.assertSetEqual(
            set([(stop['city'], stop['order']) for stop in resp.data['stops']]),
            {
                (city3.pk, 1),
            }
        )

    def test_list_unauthorized(self):
        resp = self.client.get('/rides/ride/', format='json')
        self.assertUnauthorized(resp)

    def test_list(self):
        self.authenticate()

        car = CarFactory.create(owner=self.user)
        now = timezone.now()
        tomorrow = now + timedelta(days=1)
        yesterday = now - timedelta(days=1)

        ride1 = RideFactory.create(
            number_of_seats=5,
            car=car,
            date_time=yesterday)

        ride2 = RideFactory.create(
            number_of_seats=5,
            car=car,
            date_time=tomorrow)

        resp = self.client.get('/rides/ride/', format='json')
        self.assertSuccessResponse(resp)

        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['pk'], ride2.pk)

    def test_my_unauthorized(self):
        resp = self.client.get('/rides/ride/my/', format='json')
        self.assertUnauthorized(resp)

    def test_my(self):
        self.authenticate()

        car = CarFactory.create(owner=self.user)

        my_ride_1 = RideFactory.create(
            number_of_seats=5,
            car=car)
        my_ride_2 = RideFactory.create(
            number_of_seats=5,
            car=car)

        another_user = UserFactory.create()
        another_car = CarFactory.create(owner=another_user)
        RideFactory.create(
            number_of_seats=5,
            car=another_car)

        resp = self.client.get('/rides/ride/my/', format='json')
        self.assertSuccessResponse(resp)
        self.assertSetEqual(
            {my_ride_1.pk, my_ride_2.pk},
            set([ride['pk'] for ride in resp.data['results']]))

    def test_ride_complaints_create(self):
        ride = RideFactory.create(
            number_of_seats=5,
            car=self.car)
        RideBookingFactory.create(
            ride=ride,
            client=self.user
        )

        descr_text = 'Test text'
        complaint = RideComplaintFactory.create(
            ride=ride,
            user=self.user,
            description=descr_text
        )

        self.assertEqual(complaint.user, self.user)
        self.assertEqual(complaint.description, descr_text)
        self.assertEqual(complaint.status, RideComplaintStatus.NEW)


class RideBookingViewSetTest(APITestCase):
    def setUp(self):
        super(RideBookingViewSetTest, self).setUp()
        self.city1 = CityFactory.create()
        self.city2 = CityFactory.create()

        self.car = CarFactory.create(
            owner=self.user,
            brand='some',
            model='car',
            number_of_seats=5)

        self.ride = RideFactory.create(car=self.car)
        self.booking = RideBookingFactory.create(
            ride=self.ride,
            client=self.user)

    def test_list_unauthorized(self):
        resp = self.client.get('/rides/booking/', format='json')
        self.assertUnauthorized(resp)

    def test_list(self):
        another_user = UserFactory.create(password='password')
        another_booking = RideBookingFactory.create(
            ride=self.ride,
            client=another_user)

        self.authenticate()
        resp = self.client.get('/rides/booking/', format='json')
        self.assertSuccessResponse(resp)
        self.assertListEqual([self.booking.pk],
                             [book['pk'] for book in resp.data])

        self.authenticate_as(another_user.email, 'password')
        resp = self.client.get('/rides/booking/', format='json')
        self.assertSuccessResponse(resp)
        self.assertListEqual([another_booking.pk],
                             [book['pk'] for book in resp.data])
