from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.cars.models import Car
from apps.cars.serializers import CarDetailSerializer, CarWritableSerializer
from apps.rides.models import RideStatus


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
            owner=self.request.user,
            is_deleted=False,
        )

    def perform_destroy(self, instance):
        rides = [ride for ride in instance.rides.filter(
            status=RideStatus.CREATED)]
        if rides:
            raise PermissionDenied("This car has a rides. {0}".format(rides))

        instance.is_deleted = True
        instance.save()
