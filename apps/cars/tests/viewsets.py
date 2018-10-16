from config.tests import APITestCase
from apps.places.factories import CityFactory
from apps.rides.factories import RideFactory
from apps.cars.factories import CarFactory


class CarViewSetTest(APITestCase):
    def setUp(self):
        super(CarViewSetTest, self).setUp()
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
        self.asserTrue(self.car.is_deleted)

    def test_delete_car_with_rides(self):
        self.authenticate()
        RideFactory.create(car=self.car)

        resp = self.client.delete('/rides/car/{0}/'.format(self.car.pk))
        self.assertForbidden(resp)
        self.car.refresh_from_db()
        self.assertFalse(self.car.is_deleted)
