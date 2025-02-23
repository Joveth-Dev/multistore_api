from django.db.models.query import QuerySet
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Category, Product, Store
from .permissions import IsStoreOwnerMember
from .serializers import CategorySerializer, StoreSerializer


class StoreViewSet(ModelViewSet):
    queryset = Store.objects.select_related("user", "address")
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [AllowAny]
        if self.action in ["partial_update", "update", "destroy"]:
            self.permission_classes = [IsStoreOwnerMember]
        return super().get_permissions()

    def get_serializer_context(self):
        if self.action == "create":
            return {"user": self.request.user}
        return super().get_serializer_context()


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.select_related("store")
    serializer_class = CategorySerializer
    permission_classes = [IsStoreOwnerMember]

    def get_queryset(self):
        user = self.request.user
        queryset: QuerySet = super().get_queryset()
        if self.action == "list" and not user.is_staff:
            return queryset.filter(store__user=user)
        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve"] and self.request.user.is_staff:
            self.filterset_fields = ["store__user"]
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_serializer_context(self):
        if self.action == "create":
            return {"user": self.request.user}
        return super().get_serializer_context()


# class ProductViewSet(ModelViewSet):
#     queryset = Product.objects.select_related("store")
#     serializer_class = ProductSerializer

#     def get_permissions(self):
#         if self.action in ["list", "retrieve"]:
#             self.permission_classes = [AllowAny]
#         if self.action in ["partial_update", "update", "destroy"]:
#             self.permission_classes = [IsStoreOwner]
#         return super().get_permissions()
