from rest_framework.permissions import BasePermission


class GenericModelCRUDPermission(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(view, "queryset"):
            return False
        app_label = view.queryset.model._meta.app_label
        model_name = view.queryset.model._meta.model_name
        user = request.user

        if request.method == "GET":
            return user.has_perm(f"{app_label}.view_{model_name}")
        if request.method == "POST":
            return user.has_perm(f"{app_label}.add_{model_name}")
        if request.method in ["PUT", "PATCH"]:
            return user.has_perm(f"{app_label}.change_{model_name}")
        if request.method == "DELETE":
            return user.has_perm(f"{app_label}.delete_{model_name}")


class IsStoreOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(obj.user == request.user)
