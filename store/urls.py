from rest_framework.routers import DefaultRouter

from .views import (
    CartItemViewSet,
    CartViewSet,
    CategoryViewSet,
    FeedbackViewSet,
    OrderViewSet,
    ProductViewSet,
    StoreViewSet,
)

router = DefaultRouter()

router.register("stores", StoreViewSet, basename="store")
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet),
router.register("cartitems", CartItemViewSet, basename="cartitem")
router.register("orders", OrderViewSet)
router.register("cart", CartViewSet)
router.register("feedbacks", FeedbackViewSet)

urlpatterns = router.urls
