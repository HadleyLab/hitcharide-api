from django.core.management.base import BaseCommand

from apps.accounts.factories import UserFactory
from apps.rides.factories import CarFactory, RideFactory, RideBookingFactory


class Command(BaseCommand):
    def handle(self, *args, **options):

        user1 = UserFactory.create(email='user1@example.com')
        user2 = UserFactory.create(email='user2@example.com')
        user3 = UserFactory.create(email='user3@example.com')

        car = CarFactory.create(owner=user1)

        ride = RideFactory.create(car=car, number_of_seats=4, price=100)

        RideBookingFactory.create(ride=ride, client=user2, seats_count=2)
        RideBookingFactory.create(ride=ride, client=user3)
