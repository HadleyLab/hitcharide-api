import os
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction

from apps.places.models import City, State


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        City.objects.all().delete()
        State.objects.all().delete()

        with open(os.path.join(
                settings.BASE_DIR, 'apps', 'places',
                'management', 'commands', 'usa_cities.json')) as input_file:
            data = json.load(input_file)

        for state_data in data:
            state = State.objects.create(name=state_data['name'])
            cities = []
            for city_data in state_data['cities']:
                cities.append(
                    City(
                        state=state,
                        name=city_data['name'],
                        point=Point(float(city_data['lon']),
                                    float(city_data['lat']))))

            City.objects.bulk_create(cities)
