from config.tests import APITestCase
from apps.accounts.factories import UserFactory
from apps.places.factories import CityFactory
from apps.rides.factories import RideFactory, RideBookingFactory
from apps.cars.factories import CarFactory
from apps.rides.models import RideBookingStatus
from apps.reviews.models import Review, ReviewType


class ReviewViewSetTest(APITestCase):
    def setUp(self):
        super(ReviewViewSetTest, self).setUp()
        self.city1 = CityFactory.create()
        self.city2 = CityFactory.create()
        self.car = CarFactory.create(
            owner=self.user,
            brand='some',
            model='car',
            number_of_seats=5)
        self.ride = RideFactory.create(
            car=self.car,
            city_from=self.city1,
            city_to=self.city2)
        self.passenger1 = UserFactory.create(
            email='passenger1@mail.ru',
            password='password')
        self.passenger2 = UserFactory.create(
            email='passenger2@mail.ru',
            password='password')
        RideBookingFactory.create(
            ride=self.ride,
            client=self.passenger1,
            status=RideBookingStatus.SUCCEED)
        RideBookingFactory.create(
            ride=self.ride,
            client=self.passenger2,
            status=RideBookingStatus.SUCCEED)

    def test_create_unauthorized(self):
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.passenger1.pk,
            'author_type': ReviewType.DRIVER,
            'rating': 5
        }, format='json')
        self.assertUnauthorized(resp)

    def test_create_by_owner_bad_type(self):
        self.authenticate()
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.passenger1.pk,
            'author_type': ReviewType.PASSENGER,
            'rating': 5
        }, format='json')
        self.assertBadRequest(resp)

    def test_create_by_passenger_bad_type(self):
        self.authenticate_as('passenger1@mail.ru', 'password')
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.passenger1.pk,
            'author_type': ReviewType.DRIVER,
            'rating': 5
        }, format='json')
        self.assertBadRequest(resp)

    def test_create_by_owner_bad_passenger(self):
        passenger3 = UserFactory.create()
        self.authenticate()
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': passenger3.pk,
            'author_type': ReviewType.DRIVER,
            'rating': 5
        }, format='json')
        self.assertBadRequest(resp)

    def test_create_by_owner_success(self):
        self.authenticate()
        self.assertEqual(self.passenger1.rating, 0.0)
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.passenger1.pk,
            'author_type': ReviewType.DRIVER,
            'rating': 5
        }, format='json')
        self.assertSuccessResponse(resp)

        review = Review.objects.get(pk=resp.data['pk'])
        self.assertEqual(review.author.pk, self.user.pk)
        self.assertEqual(self.passenger1.rating, 5.0)
