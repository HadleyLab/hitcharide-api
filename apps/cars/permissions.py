from rest_framework.permissions import IsAuthenticated


class IsImageOwner(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.car.owner == request.user
