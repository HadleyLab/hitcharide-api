from django.contrib.gis.db.models.functions import Distance
from django.db import models
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.geos import Point


class State(models.Model):
    name = models.CharField(
        max_length=50)

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
        return '{0}, {1}'.format(self.name, self.state.name)

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
