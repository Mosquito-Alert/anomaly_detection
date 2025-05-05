

from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from anomaly_detection.vri.models import VRI
from anomaly_detection.vri.serializers import VRISerializer


class VRIViewSet(GenericViewSet, ListModelMixin):
    """
    ViewSet for the Vector Risk Index (VRI) model.
    """
    queryset = VRI.objects.all()
    serializer_class = VRISerializer

    # TODO: Query parameters: geometry, level
    # TODO: Depending on the query parameter, return a JSON or a GeoJSON
    # TODO: Get serializer depending on the mixin (list or detail)
    # TODO: 2 actions: history and seasonality
