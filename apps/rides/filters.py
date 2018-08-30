from datetime import datetime, time

from django.utils import timezone
from rest_framework.filters import BaseFilterBackend

from .models import RidePoint


class RidesListFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        city_from = int(request.query_params.get('city_from', 0))
        if city_from:
            queryset = queryset.filter(
                stops__city_id=city_from).exclude(last_stop__city_id=city_from)

        city_to = int(request.query_params.get('city_to', 0))
        if city_to:
            queryset = queryset.filter(
                stops__city_id=city_to).exclude(first_stop__city_id=city_to)

        ride_date = request.query_params.get('date', '')
        if ride_date:
            ride_date = datetime.strptime(ride_date, '%d.%m.%Y')
            queryset = queryset.filter(
                pk__in=RidePoint.objects.filter(
                    date_time__range=(
                        datetime.combine(ride_date.date(), time.min),
                        datetime.combine(ride_date.date(), time.max)
                    )).values_list('ride_id', flat=True)
            )

        return queryset


class MyRidesFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        past = bool(request.query_params.get('past', 0))
        if past:
            queryset = queryset.filter(
                first_stop__date_time__lt=timezone.now())

        return queryset
