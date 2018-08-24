from django.test import TestCase
from django.contrib.gis.geos import Point

from apps.places.models import City
from apps.places.factories import StateFactory, CityFactory


class CityModelTestCase(TestCase):
    def setUp(self):
        krasnoyarsk = Point(92.927073, 56.016263)
        novosibirsk = Point(83.023343, 55.003334)

        state = StateFactory.create()
        self.krasnoyarsk = CityFactory.create(
            state=state,
            name='Krasnoyarsk',
            point=krasnoyarsk)
        self.novosibirsk = CityFactory.create(
            state=state,
            name='Novosibirsk',
            point=novosibirsk)

    def test_closer_to_point(self):
        kemerovo = (55.359530, 86.242738)
        lesosibirsk = (58.234978, 92.824633)
        abakan = (53.666243, 91.721903)

        self.assertEqual(
            City.closer_to_point(*kemerovo).pk,
            self.novosibirsk.pk)
        self.assertEqual(
            City.closer_to_point(*lesosibirsk).pk,
            self.krasnoyarsk.pk)
        self.assertEqual(
            City.closer_to_point(*abakan).pk,
            self.krasnoyarsk.pk)
