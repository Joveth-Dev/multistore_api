from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request


class IsStoreOwnerMember(IsAuthenticated):
    def has_permission(self, request: Request, view):
        user = request.user
        if not super().has_permission(request, view):
            return False
        if request.method == "POST":
            # Creating a new Category => needs 'add_category'
            return user.has_perm("store.add_category")

        if request.method in ["PUT", "PATCH"]:
            # Updating a Category => needs 'change_category'
            return user.has_perm("store.change_category")

        if request.method == "DELETE":
            # Deleting a Category => needs 'delete_category'
            return user.has_perm("store.delete_category")

        if request.method == "GET":
            # Reading a Category => needs 'view_category'
            # or we can skip if you want everyone to see
            return user.has_perm("store.view_category")

        return False
