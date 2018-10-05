from factory import SubFactory
from factory.django import DjangoModelFactory, ImageField

from apps.cars.factories import CarFactory
from apps.cars.models import CarImage


class CarImageFactory(DjangoModelFactory):
    car = SubFactory(CarFactory)
    image = ImageField(width=1024, height=768)

    class Meta:
        model = CarImage
