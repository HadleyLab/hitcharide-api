from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from apps.cars.models import Car
from apps.cars.serializers import CarDetailSerializer, CarWritableSerializer


class CarViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.DestroyModelMixin):
    queryset = Car.objects.all()
    serializer_class = CarDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return CarWritableSerializer
        return self.serializer_class

    def get_queryset(self):
        return super(CarViewSet, self).get_queryset().filter(
            owner=self.request.user)
