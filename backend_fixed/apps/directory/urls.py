from rest_framework.routers import DefaultRouter
from .views import WasteTypeViewSet

router = DefaultRouter()
router.register('', WasteTypeViewSet, basename='waste-type')
urlpatterns = router.urls
