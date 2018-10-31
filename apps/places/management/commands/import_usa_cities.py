import csv
import os
import gzip

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction

from apps.places.models import City, State


dataset_path = os.path.join(
    settings.BASE_DIR, 'apps', 'places', 'management', 'commands', 'dataset')


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        City.objects.all().delete()
        State.objects.all().delete()

        states = []
        with gzip.open(os.path.join(dataset_path, 'states.csv.gz'), 'rt') as fd:
            for state_data in csv.DictReader(fd):
                states.append(State(
                    name=state_data['name'],
                    short_name=state_data['short_name']))
            State.objects.bulk_create(states)

        states_mapping = {state.short_name: state.pk for state in states}

        cities = []
        with gzip.open(os.path.join(dataset_path, 'cities.csv.gz'), 'rt') as fd:
            for city_data in csv.DictReader(fd):
                cities.append(City(
                    name=city_data['name'],
                    state_id=states_mapping[city_data['state']],
                    point=Point(float(city_data['lon']),
                                float(city_data['lat']))
                ))

        City.objects.bulk_create(cities)

        print('{0} states imported'.format(len(states)))
        print('{0} cities imported'.format(len(cities)))
