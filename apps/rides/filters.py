from datetime import datetime, time

from django.utils import timezone
from rest_framework.filters import BaseFilterBackend

from .models import RideStop


class RidesListFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        city_from = int(request.query_params.get('city_from', 0))
        if city_from:
            queryset = queryset.filter(city_from=city_from)

        city_to = int(request.query_params.get('city_to', 0))
        if city_to:
            queryset = queryset.filter(city_to=city_to)

        ride_date = request.query_params.get('date', '')
        if ride_date:
            ride_date = datetime.strptime(ride_date, '%d.%m.%Y')
            queryset = queryset.filter(
                date_time__range=(
                    datetime.combine(ride_date.date(), time.min),
                    datetime.combine(ride_date.date(), time.max)
                ))

        return queryset


class MyRidesFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        past = bool(request.query_params.get('past', 0))
        if past:
            queryset = queryset.filter(
                date_time__lt=timezone.now())

        return queryset
