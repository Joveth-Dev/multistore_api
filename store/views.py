from django.db.models import Count
from django.db.models.query import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Category, Product, Store
from .permissions import IsCategoryOwner, IsProductOwner, IsStoreOwner
from .serializers import (
    CategorySerializer,
    ListAndRetrieveProductSerializer,
    ProductSerializer,
    StoreSerializer,
)


class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Store.objects.prefetch_related("user__groups").select_related(
            "user", "address"
        )
        if self.action in ["list", "retrieve"] and not self.request.user.is_staff:
            queryset = queryset.annotate(product_count=Count("product")).filter(
                product_count__gt=0, is_live=True
            )
        return queryset

    def get_permissions(self):
        user_groups = self.get_user_groups()
        if self.action == "my_store":
            if "Store Owner" not in user_groups:
                raise PermissionDenied("You must own a store!")
        if self.action == "create":
            if self.request.user.is_staff:
                raise PermissionDenied("Admins cannot create a store!")
            if "Store Owner" in user_groups:
                raise PermissionDenied("You're already a store owner!")
            self.permission_classes = [IsAuthenticated]
        if self.action in ["list", "retrieve"]:
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
        store = Store.objects.get(user=request.user)
        return Response(self.get_serializer(store).data, status=status.HTTP_200_OK)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.prefetch_related(
            Prefetch("store__user__groups")
        ).select_related("store__user", "store__address")
        if user.is_staff:
            return queryset
        return queryset.filter(store__user=user)

    def get_permissions(self):
        if self.action == "create":
            user_groups = self.get_user_groups()
            if "Store Owner" not in user_groups:
                raise PermissionDenied()
        if self.action in ["partial_update", "update", "destroy"]:
            self.permission_classes = [IsCategoryOwner | IsAdminUser]
        return super().get_permissions()

    def get_serializer_context(self):
        return {"user": self.request.user}

    def get_user_groups(self):
        user = self.request.user
        user_groups = getattr(user, "_cached_groups", None)
        if user_groups is None:
            user_groups = set(user.groups.values_list("name", flat=True))
            setattr(user, "_cached_groups", user_groups)
        return user_groups


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related(
        Prefetch("store__user__groups")
    ).select_related("store__user", "store__address", "category")
    serializer_class = ProductSerializer
    filterset_fields = ["store"]
    pagination_class = None

    def get_permissions(self):
        if self.action in ["create", "my_products"]:
            user_groups = self.get_user_groups()
            if "Store Owner" not in user_groups:
                raise PermissionDenied()
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [AllowAny]
        if self.action in ["partial_update", "update", "destroy"]:
            self.permission_classes = [IsProductOwner | IsAdminUser]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "my_products"]:
            self.serializer_class = ListAndRetrieveProductSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        response_serializer = ListAndRetrieveProductSerializer(
            product, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        # Serialize again using ListAndRetrieveProductSerializer for the response
        response_serializer = ListAndRetrieveProductSerializer(
            instance, context=self.get_serializer_context()
        )

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {"user": self.request.user}

    def get_user_groups(self):
        user = self.request.user
        user_groups = getattr(user, "_cached_groups", None)
        if user_groups is None:
            user_groups = set(user.groups.values_list("name", flat=True))
            setattr(user, "_cached_groups", user_groups)
        return user_groups

    @action(detail=False, methods=["GET"])
    def my_products(self, request):
        products = self.get_queryset().filter(store__user=request.user)
        return Response(
            self.get_serializer(products, many=True).data, status=status.HTTP_200_OK
        )
