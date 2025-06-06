"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularJSONAPIView,
                                   SpectacularRedocView,
                                   SpectacularSwaggerView)

from django.conf import settings

base_url = "api/v1"

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{base_url}/schema/openapi.yml', SpectacularAPIView.as_view(api_version='v1'), name='api-schema'),
    path(f'{base_url}/schema/openapi.json', SpectacularJSONAPIView.as_view(api_version='v1'), name='api-schema-json'),
    path(
        f'{base_url}/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema',),
        name='swagger-ui'
    ),
    path(f'{base_url}/docs/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='redoc'),
    path(f'{base_url}/', include('anomaly_detection.predictions.urls', namespace='predictions')),
    path(f'{base_url}/', include('anomaly_detection.regions.urls', namespace='regions')),
]


if settings.DEBUG:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
