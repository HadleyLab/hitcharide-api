from factory import DjangoModelFactory, fuzzy, SubFactory
from django.contrib.gis.geos import Point

from .models import State, City


class StateFactory(DjangoModelFactory):
    name = fuzzy.FuzzyText()

    class Meta:
        model = State


class CityFactory(DjangoModelFactory):
    name = fuzzy.FuzzyText()
    state = SubFactory(StateFactory)
    point = Point(0, 0)

    class Meta:
        model = City
