from rest_framework.routers import DefaultRouter

from .views import CartItemViewSet, CategoryViewSet, ProductViewSet, StoreViewSet

router = DefaultRouter()

router.register("stores", StoreViewSet, basename="store")
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet),
router.register("cartitems", CartItemViewSet, basename="cartitem")

urlpatterns = router.urls
