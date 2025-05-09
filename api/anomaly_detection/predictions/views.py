from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from vectortiles.mixins import BaseVectorTileView
from vectortiles.rest_framework.renderers import MVTRenderer

from anomaly_detection.predictions.models import Metric
from anomaly_detection.predictions.serializers import MetricSerializer
from anomaly_detection.predictions.vector_layers import MetricMunicipalityVectorLayer


class MetricViewSet(BaseVectorTileView, GenericViewSet, ListModelMixin):
    """
    ViewSet for Metric model.
    """
    queryset = Metric.objects
    serializer_class = MetricSerializer
    layer_classes = [MetricMunicipalityVectorLayer]

    id = "features"
    tile_fields = ('anomaly_degree', )

    @action(detail=False, methods=['get'], renderer_classes=(MVTRenderer, ),
            url_path='tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).pbf', url_name='tile')
    def tile(self, request, z, x, y, *args, **kwargs):
        z, x, y = int(z), int(x), int(y)
        content, status = self.get_content_status(z, x, y)
        return Response(content, status=status)

    def get_queryset(self):
        """
        Override the get_queryset method to filter the queryset based on
        the method action and the request parameters.
        """
        queryset = super().get_queryset()

        if self.action == 'list':
            # Get the most recent date in the queryset
            if latest_date := queryset.values('date').order_by('-date').first()['date']:
                # Filter the queryset to include only the latest date
                queryset = queryset.filter(date=latest_date)
            else:
                queryset = queryset.none()
        return queryset.order_by()

    def get_serializer_class(self):
        """
        Override the get_serializer_class method to return the appropriate
        serializer class based on the method action and the request parameters.
        """
        return super().get_serializer_class()

    # TODO: Query parameters: geometry, level
    # TODO: Depending on the query parameter, return a JSON or a GeoJSON
    # TODO: Get serializer depending on the mixin (list or detail)
    # TODO: 2 actions: history and seasonality
