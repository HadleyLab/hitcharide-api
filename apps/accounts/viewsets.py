from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer


class UserDetailViewSet(mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
