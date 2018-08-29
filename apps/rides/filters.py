from datetime import datetime, time

from django.db.models import Count, F
from django.utils import timezone
from rest_framework.filters import BaseFilterBackend

from .models import RidePoint


class RidesFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        past = bool(request.query_params.get('past', 0))
        if past:
            queryset = queryset.filter(
                pk__in=RidePoint.objects.filter(
                    date_time__lt=timezone.now(),
                    order=0).values_list('ride_id', flat=True)
            )

        city_from = int(request.query_params.get('city_from', 0))
        if city_from:
            # queryset = queryset.annotate(stops_count=Count('stops')).filter(
            #     stops__city=city_from,
            #     stops__order__lt=F('stops_count'))
            print(str(queryset.query))
            queryset = queryset.filter(
                pk__in=RidePoint.objects.annotate(stops_count=Count('ride__stops')).filter(
                    city_id=city_from,
                    order__lt=F('stops_count') - 1).values_list('ride_id', flat=True)
            )  # NOTE: We need to filter not last in this list, so lets orient
            print(str(queryset.query))

        city_to = int(request.query_params.get('city_to', 0))
        if city_to:
            queryset = queryset.filter(
                pk__in=RidePoint.objects.filter(
                    city_id=city_to,
                    order__gt=0).values_list('ride_id', flat=True)
            )

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
