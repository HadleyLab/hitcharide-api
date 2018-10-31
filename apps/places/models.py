from django.contrib.gis.db.models.functions import Distance
from django.db import models
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.geos import Point


class State(models.Model):
    name = models.CharField(
        max_length=50)
    short_name = models.CharField(
        max_length=2)

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='cities')
    name = models.CharField(
        max_length=80)
    point = geo_models.PointField()

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.state.short_name)

    @classmethod
    def closer_to_point(cls, lat, lon):
        point = Point(lon, lat, srid=4326)
        return cls.objects.annotate(
            distance=Distance('point', point)
        ).order_by('distance').first()

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        unique_together = ('state', 'name')


class PlaceCategory(object):
    TRAIN_STATION = 'ts'
    BUS_STATION = 'bs'
    AIRPORT = 'a'
    EDUCATIONAL_PLACE = 'ep'

    CHOICES = (
        (TRAIN_STATION, 'Train station'),
        (BUS_STATION, 'Bus station'),
        (AIRPORT, 'Airport'),
        (EDUCATIONAL_PLACE, 'Education place'),
    )


class Place(models.Model):
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='places')
    name = models.CharField(
        max_length=120)
    short_name = models.CharField(
        max_length=80)
    point = geo_models.PointField()
    category = models.CharField(
        max_length=2,
        choices=PlaceCategory.CHOICES)

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.city)
