from rest_framework import viewsets, mixins

from apps.cars.models import Car, CarImage
from apps.cars.permissions import IsImageOwner
from apps.cars.serializers.car_image import CarImageDetailSerializer, \
    CarImageWritableSerializer


class CarImageViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin):
    queryset = CarImage.objects.all()
    serializer_class = CarImageDetailSerializer
    permission_classes = (IsImageOwner,)

    def get_serializer_class(self):
        if self.action in ['create']:
            return CarImageWritableSerializer
        return self.serializer_class

    def get_queryset(self):
        qs = super(CarImageViewSet, self).get_queryset()

        return qs.filter(car=self.get_car_pk())

    def get_car_pk(self):
        return self.kwargs['car_pk']

    def get_car(self):
        return Car.objects.get(pk=self.get_car_pk())

    def perform_create(self, serializer):
        return serializer.save(car=self.get_car())
