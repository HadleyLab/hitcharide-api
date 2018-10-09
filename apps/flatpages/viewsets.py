from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny

from .models import FlatPage
from .serializers import FlatPageSerializer


class FlatPageViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin):
    queryset = FlatPage.objects.all()
    serializer_class = FlatPageSerializer
    permission_classes = (AllowAny,)
