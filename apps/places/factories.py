from factory import DjangoModelFactory, fuzzy, SubFactory

from .models import State, City


class StateFactory(DjangoModelFactory):
    name = fuzzy.FuzzyText()

    class Meta:
        model = State


class CityFactory(DjangoModelFactory):
    name = fuzzy.FuzzyText()
    state = SubFactory(StateFactory)

    class Meta:
        model = City
