

from rest_framework.routers import DefaultRouter

from anomaly_detection.vri import views


router = DefaultRouter()

router.register('vri', views.VRIViewSet, basename='vri')

app_name = 'vri'

urlpatterns = router.urls
