from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import User
from apps.cars.serializers import UserWithCarsSerializer


class UserDetailViewSet(mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserWithCarsSerializer
    permission_classes = (IsAuthenticated,)
