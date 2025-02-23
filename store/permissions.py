from rest_framework.permissions import BasePermission

from .models import Store


class IsStoreOwner(BasePermission):
    def has_object_permission(self, request, view, obj: Store):
        return obj.user == request.user