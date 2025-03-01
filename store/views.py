from django.db.models import Count
from django.db.models.query import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Category, Store
from .permissions import IsStoreOwner
from .serializers import CategorySerializer, StoreSerializer


class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer

    def get_queryset(self):
        if self.action in ["partial_update", "update"]:
            user_groups = self.get_user_groups()
            if "Store Owner" in user_groups:
                queryset = Store.objects.filter(user=self.request.user)
        else:
            queryset = (
                Store.objects.annotate(product_count=Count("product"))
                .filter(product_count__gt=0)
                .prefetch_related("user__groups")
                .select_related("user", "address")
            )
        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            self.permission_classes = [AllowAny]
        if self.action in ["partial_update", "update", "destroy"]:
            self.permission_classes = [IsStoreOwner | IsAdminUser]
        return super().get_permissions()

    def get_serializer_context(self):
        if self.action == "create":
            return {"user": self.request.user}
        return super().get_serializer_context()

    def get_user_groups(self):
        user = self.request.user
        user_groups = getattr(user, "_cached_groups", None)
        if user_groups is None:
            user_groups = set(user.groups.values_list("name", flat=True))
            setattr(user, "_cached_groups", user_groups)
        return user_groups

    @action(detail=False, methods=["GET"])
    def my_store(self, request):
        user_groups = self.get_user_groups()
        if "Store Owner" in user_groups:
            store = Store.objects.get(user=request.user)
            return Response(self.get_serializer(store).data, status=status.HTTP_200_OK)
        raise PermissionDenied()


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.prefetch_related(
            Prefetch("store__user__groups")
        ).select_related("store__user")
        if user.is_staff:
            if self.action == "create":
                raise PermissionDenied("Admins are not allowed to create categories.")
            return queryset
        return queryset.filter(store__user=user)

    def get_permissions(self):
        user = self.request.user
        user_groups = self.get_user_groups()
        if "Store Owner" not in user_groups and not user.is_staff:
            raise PermissionDenied()
        if user.is_staff and self.action == "create":
            raise PermissionDenied()
        return super().get_permissions()

    def get_serializer_context(self):
        return (
            {"user": self.request.user}
            if self.action == "create"
            else super().get_serializer_context()
        )

    def get_user_groups(self):
        user = self.request.user
        user_groups = getattr(user, "_cached_groups", None)
        if user_groups is None:
            user_groups = set(user.groups.values_list("name", flat=True))
            setattr(user, "_cached_groups", user_groups)
        return user_groups


# class ProductViewSet(ModelViewSet):
#     queryset = Product.objects.select_related("store")
#     serializer_class = ProductSerializer

#     def get_permissions(self):
#         if self.action in ["list", "retrieve"]:
#             self.permission_classes = [AllowAny]
#         if self.action in ["partial_update", "update", "destroy"]:
#             self.permission_classes = [IsStoreOwner]
#         return super().get_permissions()
