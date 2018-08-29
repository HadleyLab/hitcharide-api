from django.db import models
from rest_framework import viewsets, response


class CreatedUpdatedMixin(models.Model):
    created = models.DateTimeField(
        auto_now_add=True)
    updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        abstract = True


class ListFactoryMixin(viewsets.GenericViewSet):
    """
    Mixin provides method list_factory, that generates list method such as
    rest_framework.mixins.ListModelMixin.list with custom queryset
    """
    def list_factory(self, queryset, serializer_kwargs=None):
        if serializer_kwargs is None:
            serializer_kwargs = {}

        def _list(request, *args, **kwargs):
            qs = self.filter_queryset(queryset)

            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(
                qs, many=True, **serializer_kwargs)
            return response.Response(serializer.data)

        return _list
