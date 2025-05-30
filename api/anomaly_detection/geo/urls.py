

from rest_framework.routers import DefaultRouter

from anomaly_detection.geo import views

router = DefaultRouter()

router.register('regions', views.RegionViewSet, basename='regions')

app_name = 'regions'

urlpatterns = router.urls
