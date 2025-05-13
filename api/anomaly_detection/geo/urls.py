

from django.urls import path
# from rest_framework.routers import DefaultRouter

from anomaly_detection.geo.views import GEOViewSet

app_name = 'geo'

urlpatterns = [
    path('geo/tiles/<int:z>/<int:x>/<int:y>', GEOViewSet.as_view(), name='geo-region'),
]
