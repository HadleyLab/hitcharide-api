from factory import fuzzy, post_generation, SubFactory
from factory.django import DjangoModelFactory, ImageField

from apps.accounts.factories import UserFactory
from apps.cars.models import Car


class CarFactory(DjangoModelFactory):
    owner = SubFactory(UserFactory)
    brand = fuzzy.FuzzyText()
    model = fuzzy.FuzzyText()
    color = fuzzy.FuzzyText()
    license_plate = fuzzy.FuzzyText()
    number_of_seats = fuzzy.FuzzyInteger(low=2, high=7)
    photo = ImageField(width=1024, height=768)

    class Meta:
        model = Car

    @post_generation
    def add_images(self, create, extracted, **kwargs):
        from .car_image import CarImageFactory

        if not create:
            return

        if extracted:
            CarImageFactory.create(
                car=self
            )
