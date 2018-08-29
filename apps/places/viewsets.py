from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from config.pagination import DefaultPageNumberPagination
from .models import State, City
from .serializers import StateSerializer, CitySerializer, \
    CityWithStateSerializer


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
