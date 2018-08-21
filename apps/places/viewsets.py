from rest_framework import viewsets, mixins

from .models import State
from .serializers import StateSerializer


class StatesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = State.objects.all()
    serializer_class = StateSerializer
