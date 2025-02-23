from rest_framework.routers import DefaultRouter

from .views import StoreViewSet

router = DefaultRouter()

router.register("stores", StoreViewSet)

urlpatterns = router.urls
