from rest_framework import viewsets, mixins

from .models import FlatPage
from .serializers import FlatPageSerializer


class FlatPageViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin):
    queryset = FlatPage.objects.all()
    serializer_class = FlatPageSerializer
