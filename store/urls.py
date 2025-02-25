from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, StoreViewSet

router = DefaultRouter()

router.register("stores", StoreViewSet, basename="store")
router.register("categories", CategoryViewSet, basename="category")
# router.register("products", ProductViewSet)

urlpatterns = router.urls
