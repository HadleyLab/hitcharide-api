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

    def get_ride_request_data(self):
        return {
            'city_from': self.city1.pk,
            'city_to': self.city2.pk,
            'date_time': timezone.now() + timedelta(days=1),
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

        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['pk'], ride2.pk)

    def test_list_filter_by_city_to(self):
        self.authenticate()
        now = timezone.now()
        tomorrow = now + timedelta(days=1)

        car = CarFactory.create(owner=self.user)
        ride1 = RideFactory.create(
            city_from=self.city1,
            city_to=self.city2,
            car=car,
            date_time=tomorrow)

        ride2 = RideFactory.create(
            car=car,
            date_time=tomorrow,
            stops_cities=[self.city2])

        ride3 = RideFactory.create(
            car=car,
            date_time=tomorrow)

        resp = self.client.get(
            '/rides/ride/', {'city_to': self.city1.pk}, format='json')
        self.assertSuccessResponse(resp)
        self.assertEqual(len(resp.data), 0)

        resp = self.client.get(
            '/rides/ride/', {'city_to': self.city2.pk}, format='json')
        self.assertSuccessResponse(resp)
        self.assertEqual(len(resp.data), 2)
        self.assertSetEqual(
            {ride1.pk, ride2.pk},
            set([ride['pk'] for ride in resp.data]))

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
            set([ride['pk'] for ride in resp.data]))

    def test_ride_complaints_create(self):
        ride = RideFactory.create(
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

    @mock.patch('apps.rides.utils.ride_booking_refund', autospec=True)
    def test_cancel_ride_by_driver(self, mock_ride_booking_refund):
        self.authenticate()
        ride = RideFactory.create(car=self.car)
        booking = RideBookingFactory.create(
            ride=ride,
            client=self.user)
        payed_booking = RideBookingFactory.create(
            ride=ride,
            client=self.user,
            status=RideBookingStatus.PAYED)
        canceled_booking = RideBookingFactory.create(
            ride=ride,
            client=self.user,
            status=RideBookingStatus.CANCELED)
        reason_text = 'test reason'

        self.assertEqual(ride.status, RideStatus.CREATED)
        resp = self.client.post(
            '/rides/ride/{0}/cancel/'.format(ride.pk),
            {
                'cancel_reason': reason_text
            })

        self.assertSuccessResponse(resp)
        self.assertEqual(mock_ride_booking_refund.call_count, 1)
        mock_ride_booking_refund.assert_called_with(payed_booking)

        booking.refresh_from_db()
        payed_booking.refresh_from_db()
        canceled_booking.refresh_from_db()
        ride.refresh_from_db()

        self.assertEqual(booking.status, RideBookingStatus.REVOKED)
        self.assertEqual(payed_booking.status, RideBookingStatus.REVOKED)
        self.assertEqual(canceled_booking.status, RideBookingStatus.CANCELED)
        self.assertEqual(ride.status, RideStatus.CANCELED)
        self.assertEqual(ride.cancel_reason, reason_text)


class RideBookingViewSetTest(APITestCase):
    def setUp(self):
        super(RideBookingViewSetTest, self).setUp()
        self.city1 = CityFactory.create()
        self.city2 = CityFactory.create()

        self.car = CarFactory.create(owner=self.user)

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

    @mock.patch('apps.rides.viewsets.ride_booking_refund', autospec=True)
    def test_cancel_payed_booking_by_passenger(self, mock_ride_booking_refund):
        self.authenticate()
        ride = RideFactory.create(
            car=self.car)
        payed_booking = RideBookingFactory.create(
            ride=ride,
            client=self.user,
            status=RideBookingStatus.PAYED)
        cancel_reason = 'test reason'

        resp = self.client.post(
            '/rides/booking/{0}/cancel/'.format(
                payed_booking.pk),
            {'cancel_reason': cancel_reason})
        self.assertSuccessResponse(resp)
        self.assertEqual(mock_ride_booking_refund.call_count, 1)
        mock_ride_booking_refund.assert_called_with(payed_booking)

        payed_booking.refresh_from_db()
        self.assertEqual(payed_booking.status, RideBookingStatus.CANCELED)
        self.assertEqual(payed_booking.cancel_reason, cancel_reason)

    @mock.patch('apps.rides.viewsets.ride_booking_refund', autospec=True)
    def test_cancel_created_booking_by_passenger(self, mock_ride_booking_refund):
        self.authenticate()
        ride = RideFactory.create(
            car=self.car)
        booking = RideBookingFactory.create(
            ride=ride,
            client=self.user,
            status=RideBookingStatus.CREATED)
        cancel_reason = 'test reason'

        resp = self.client.post(
            '/rides/booking/{0}/cancel/'.format(
                booking.pk),
            {'cancel_reason': cancel_reason})
        self.assertSuccessResponse(resp)
        self.assertEqual(mock_ride_booking_refund.call_count, 0)

        booking.refresh_from_db()
        self.assertEqual(booking.status, RideBookingStatus.CANCELED)
        self.assertEqual(booking.cancel_reason, cancel_reason)
