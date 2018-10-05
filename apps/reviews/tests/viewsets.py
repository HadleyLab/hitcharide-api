from config.tests import APITestCase
from apps.accounts.factories import UserFactory
from apps.places.factories import CityFactory
from apps.rides.factories import RideFactory, RideBookingFactory
from apps.cars.factories import CarFactory
from apps.rides.models import RideBookingStatus
from apps.reviews.models import Review, ReviewAuthorType
from apps.reviews.factories import ReviewFactory


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
            status=RideBookingStatus.PAYED)
        RideBookingFactory.create(
            ride=self.ride,
            client=self.passenger2,
            status=RideBookingStatus.PAYED)

    def test_create_unauthorized(self):
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.passenger1.pk,
            'author_type': ReviewAuthorType.DRIVER,
            'rating': 5
        }, format='json')
        self.assertUnauthorized(resp)

    def test_create_by_owner_bad_type(self):
        self.authenticate()
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.passenger1.pk,
            'author_type': ReviewAuthorType.PASSENGER,
            'rating': 5
        }, format='json')
        self.assertBadRequest(resp)

    def test_create_by_passenger_bad_type(self):
        self.authenticate_as('passenger1@mail.ru', 'password')
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.passenger1.pk,
            'author_type': ReviewAuthorType.DRIVER,
            'rating': 5
        }, format='json')
        self.assertBadRequest(resp)

    def test_create_by_owner_bad_passenger(self):
        passenger3 = UserFactory.create()
        self.authenticate()
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': passenger3.pk,
            'author_type': ReviewAuthorType.DRIVER,
            'rating': 5
        }, format='json')
        self.assertBadRequest(resp)

    def test_create_by_passenger_about_passenger(self):
        self.authenticate_as('passenger1@mail.ru', 'password')
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.passenger2.pk,
            'author_type': ReviewAuthorType.PASSENGER,
            'rating': 5
        }, format='json')
        self.assertBadRequest(resp)

    def test_create_by_author_about_myself(self):
        self.authenticate()
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.user.pk,
            'author_type': ReviewAuthorType.DRIVER,
            'rating': 5
        }, format='json')
        self.assertBadRequest(resp)

    def test_create_by_passenger_about_myself(self):
        self.authenticate_as('passenger1@mail.ru', 'password')
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.passenger1.pk,
            'author_type': ReviewAuthorType.PASSENGER,
            'rating': 5
        }, format='json')
        self.assertBadRequest(resp)

    def test_create_by_owner_success(self):
        self.authenticate()
        self.assertEqual(self.passenger1.get_rating()['value'], 0.0)
        resp = self.client.post('/reviews/', {
            'ride': self.ride.pk,
            'subject': self.passenger1.pk,
            'author_type': ReviewAuthorType.DRIVER,
            'rating': 5
        }, format='json')
        self.assertSuccessResponse(resp)

        review = Review.objects.get(pk=resp.data['pk'])
        self.assertEqual(review.author.pk, self.user.pk)
        self.assertEqual(self.passenger1.get_rating()['value'], 5.0)

    def test_list_unauthorized(self):
        resp = self.client.get('/reviews/')
        self.assertUnauthorized(resp)

    def _create_reviews(self):
        self.review1 = ReviewFactory.create(
            author=self.user,
            ride=self.ride,
            subject=self.passenger1,
            author_type=ReviewAuthorType.DRIVER,
            rating=3,
            comment='Always crying and smells like ....')
        self.review2 = ReviewFactory.create(
            author=self.user,
            ride=self.ride,
            subject=self.passenger2,
            author_type=ReviewAuthorType.DRIVER,
            rating=5,
            comment='Nice passenger!')

        self.review3 = ReviewFactory.create(
            author=self.passenger1,
            ride=self.ride,
            subject=self.user,
            author_type=ReviewAuthorType.PASSENGER,
            rating=2,
            comment='Always screaming on me!')
        self.review4 = ReviewFactory.create(
            author=self.passenger2,
            ride=self.ride,
            subject=self.user,
            author_type=ReviewAuthorType.PASSENGER,
            rating=5,
            comment='Nice driver!')

    def test_list_ride(self):
        self._create_reviews()
        self.authenticate()
        new_car = CarFactory.create(owner=UserFactory.create())
        new_ride = RideFactory.create(car=new_car)

        resp = self.client.get('/reviews/?ride={0}'.format(new_ride.pk))
        self.assertSuccessResponse(resp)
        self.assertEqual(len(resp.data), 0)

        resp = self.client.get('/reviews/?ride={0}'.format(self.ride.pk))
        self.assertSuccessResponse(resp)
        self.assertEqual(len(resp.data), 4)
        self.assertSetEqual(
            set([item['pk'] for item in resp.data]),
            {self.review1.pk, self.review2.pk, self.review3.pk, self.review4.pk}
        )
        self.assertEqual(self.user.get_rating()['value'], 3.5)

    def test_list_author(self):
        self._create_reviews()
        self.authenticate()
        resp = self.client.get('/reviews/?author={0}'.format(self.user.pk))
        self.assertEqual(len(resp.data), 2)
        self.assertSetEqual(
            set([item['pk'] for item in resp.data]),
            {self.review1.pk, self.review2.pk})

    def test_list_subject(self):
        self._create_reviews()
        self.authenticate()
        resp = self.client.get('/reviews/?subject={0}'.format(self.user.pk))
        self.assertEqual(len(resp.data), 2)
        self.assertSetEqual(
            set([item['pk'] for item in resp.data]),
            {self.review3.pk, self.review4.pk})
