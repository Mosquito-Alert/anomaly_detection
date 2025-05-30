from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from vectortiles.mixins import BaseVectorTileView
from vectortiles.rest_framework.renderers import MVTRenderer

from anomaly_detection.geo.models import Municipality
from anomaly_detection.geo.serializers import MunicipalitySerializer
from anomaly_detection.geo.vector_layers import MunicipalityVectorLayer, ProvinceVectorLayer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='region_name',
                type=OpenApiTypes.STR,
                description='Region name.',
                required=False,
                default='Lloret de Mar'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=['name', '-name', 'province', '-province', 'code', '-name',],
                description='Order by `code`, `name` or `province`.',
            ),

        ]
    ),
)
class RegionViewSet(BaseVectorTileView, GenericViewSet, ListModelMixin):
    """
    ViewSet for the Municipality model with MVT rendering.
    """
    queryset = Municipality.objects.all()  # .with_geometry().all()
    layer_classes = [MunicipalityVectorLayer, ProvinceVectorLayer]
    serializer_class = MunicipalitySerializer

    def get_queryset(self):
        """
        Override the default queryset to filter by region name if provided.
        """
        queryset = super().get_queryset()
        region_name = self.request.query_params.get('region_name', None)
        if region_name:
            queryset = queryset.filter(name__icontains=region_name)
        return queryset

    @action(
        methods=['GET'],
        detail=False,
        renderer_classes=(MVTRenderer, ),
        url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)',  # TODO: Remove trailing slash (only in this method)
        url_name='tiles')
    def get_tiles(self, request, z, x, y, *args, **kwargs):
        """
        Action that returns the tiles of a specified area and zoom
        """
        z, x, y = int(z), int(x), int(y)
        content, status = self.get_content_status(z, x, y)
        return Response(content, status=status)
