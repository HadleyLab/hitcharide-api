import os
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from apps.places.models import City, State


class Command(BaseCommand):

    def handle(self, *args, **options):
        City.objects.all().delete()
        State.objects.all().delete()

        data = json.loads(
            open(os.path.join(
                settings.BASE_DIR, 'apps', 'places',
                'management', 'commands', 'usa_cities.json')).read())

        for state_data in data:
            state = State.objects.create(name=state_data['name'])
            for city_data in state_data['cities']:
                City.objects.create(
                    state=state,
                    name=city_data['name'],
                    point=Point(float(city_data['lon']),
                                float(city_data['lat'])))
