from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from .models import Store
from .permissions import IsStoreOwner
from .serializers import StoreSerializer


class StoreViewSet(ModelViewSet):
    queryset = Store.objects.select_related("user", "address")
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [AllowAny]
        if self.action in ["partial_update", "update", "destroy"]:
            self.permission_classes = [IsStoreOwner]
        return super().get_permissions()

    def get_serializer_context(self):
        if self.action == "create":
            return {"user": self.request.user}
        return super().get_serializer_context()
