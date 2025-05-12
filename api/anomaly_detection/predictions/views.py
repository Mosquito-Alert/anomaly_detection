from datetime import datetime
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from vectortiles.mixins import BaseVectorTileView
from vectortiles.rest_framework.renderers import MVTRenderer

from anomaly_detection.predictions.models import Metric
from anomaly_detection.predictions.serializers import MetricSerializer
from anomaly_detection.predictions.vector_layers import MetricMunicipalityVectorLayer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='date_from',
                type=OpenApiTypes.DATE,
                description='Starting date which the results will return.',
                required=False,
                default=datetime.today().strftime('%Y-%m-%d')
            ),
            OpenApiParameter(
                name='date_to',
                type=OpenApiTypes.DATE,
                description='Ending date which the results will return.',
                required=False,
                default=datetime.today().strftime('%Y-%m-%d')
            ),
            OpenApiParameter(
                name='region_code',
                type=OpenApiTypes.STR,
                description='Determines the region of the results (history).',
                required=False,
                default='ESP.1.1.1.1_1'
            ),

        ]
    ),
    tiles=extend_schema(
        parameters=[
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                description='Date of the results to return.',
                required=True,
                default=datetime.today().strftime('%Y-%m-%d')
            ),

        ]
    )
)
class MetricViewSet(BaseVectorTileView, GenericViewSet, ListModelMixin):
    """
    ViewSet for Metric model.
    """
    queryset = Metric.objects
    serializer_class = MetricSerializer
    layer_classes = [MetricMunicipalityVectorLayer]

    id = "features"
    tile_fields = ('anomaly_degree', )

    def get_layer_class_kwargs(self):
        return {'date': self.request.query_params.get('date')}

    def get_layers(self):
        try:
            return super().get_layers()
        except ValueError as e:
            raise ValidationError(e)

    @action(
        detail=False,
        methods=['get'],
        renderer_classes=(MVTRenderer, ),
        url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).pbf',
        url_name='tiles')
    def tiles(self, request, z, x, y, *args, **kwargs):
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
            date_from = self.request.query_params.get('date_from')
            date_to = self.request.query_params.get('date_to')
            region_code = self.request.query_params.get('region_code')
            if date_from:
                queryset = queryset.filter(date__gte=date_from)
            if date_to:
                queryset = queryset.filter(date__lte=date_to)
            if region_code:
                queryset = queryset.filter(region__code=region_code)

        #     # ! return queryset.order_by()
        return queryset

    def get_serializer_class(self):
        """
        Override the get_serializer_class method to return the appropriate
        serializer class based on the method action and the request parameters.
        """
        return super().get_serializer_class()
