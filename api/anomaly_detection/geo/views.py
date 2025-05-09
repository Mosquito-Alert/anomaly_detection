from vectortiles.rest_framework.views import MVTAPIView

from anomaly_detection.geo.models import Municipality
from anomaly_detection.geo.vector_layers import MunicipalityVectorLayer, ProvinceVectorLayer


class GEOViewSet(MVTAPIView):
    """
    ViewSet for the Municipality model with MVT rendering.
    """
    queryset = Municipality.objects.with_geometry().all()
    layer_classes = [MunicipalityVectorLayer, ProvinceVectorLayer]
