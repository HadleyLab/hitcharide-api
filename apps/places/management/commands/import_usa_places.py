import os
import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction

from apps.places.models import State, Place, PlaceCategory


dataset_path = os.path.join(settings.BASE_DIR, 'dataset')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # Preload states with cities
        self.states_mapping = {
            state.short_name: {city.name.lower(): city.pk
                               for city in state.cities.all()}
            for state in State.objects.prefetch_related('cities')}

    def import_category(self, category, filename):
        places = []
        with open(os.path.join(dataset_path, filename)) as fd:
            for place_data in csv.DictReader(fd):
                cities_mapping = self.states_mapping[place_data['state']]
                city = cities_mapping.get(place_data['city'].lower())

                places.append(
                    Place(
                        name=place_data['name'],
                        city_id=city,
                        category=category,
                        short_name=place_data['short_name'],
                        point=Point(
                            float(place_data['lon']),
                            float(place_data['lat'])
                        )
                    )
                )

        Place.objects.bulk_create(places)
        print('{0} places with category `{1}` imported'.format(
            len(places), category))

    @transaction.atomic
    def handle(self, *args, **options):
        Place.objects.all().delete()

        files_by_category = [
            (PlaceCategory.AIRPORT, 'airports.csv'),
            (PlaceCategory.BUS_STATION, 'bus_stations.csv'),
            (PlaceCategory.TRAIN_STATION, 'train_stations.csv'),
            (PlaceCategory.EDUCATIONAL_PLACE, 'educational_places.csv'),
        ]
        for category, filename in files_by_category:
            self.import_category(category, filename)
