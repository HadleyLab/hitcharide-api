from django.db.models import Case, When, PositiveSmallIntegerField
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from config.pagination import DefaultPageNumberPagination
from .models import State, City, Place, PlaceCategory
from .serializers import StateSerializer, CitySerializer, \
    CityWithStateSerializer, PlaceSerializer


class StateViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = State.objects.all()
    serializer_class = StateSerializer

    @action(methods=['GET'], detail=True)
    def cities(self, request, pk):
        state = self.get_object()
        return Response(CitySerializer(state.cities.all(), many=True).data)


class CityViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = City.objects.all().select_related('state').order_by('name')
    serializer_class = CityWithStateSerializer
    pagination_class = DefaultPageNumberPagination
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    filter_fields = ('state',)


class PlaceViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    pagination_class = DefaultPageNumberPagination
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('name', 'short_name',)
    filter_fields = ('city', 'category',)

    def get_queryset(self):
        queryset = super(PlaceViewSet, self).get_queryset()

        return queryset.annotate(
            sortable_category=Case(
                When(category=PlaceCategory.AIRPORT, then=1),
                When(category=PlaceCategory.BUS_STATION, then=2),
                When(category=PlaceCategory.TRAIN_STATION, then=3),
                When(category=PlaceCategory.EDUCATIONAL_PLACE, then=4),
                default=0,
                output_field=PositiveSmallIntegerField()
            )
        ).order_by('sortable_category', 'name')
