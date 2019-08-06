from rest_framework.routers import SimpleRouter

from garage.views import CarViewSet

router = SimpleRouter()
router.register('cars', CarViewSet)
urlpatterns = router.urls


