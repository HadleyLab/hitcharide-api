from factory import DjangoModelFactory

from .models import Review


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review
