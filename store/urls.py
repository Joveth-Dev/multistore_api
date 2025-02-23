from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, StoreViewSet

router = DefaultRouter()

router.register("stores", StoreViewSet)
router.register("categories", CategoryViewSet)
# router.register("products", ProductViewSet)

urlpatterns = router.urls
