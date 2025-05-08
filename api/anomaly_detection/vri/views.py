

from enum import Enum
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from anomaly_detection.vri.models import VRI
from anomaly_detection.vri.serializers import GeoVRISerializer, VRISerializer


class FormatEnum(str, Enum):
    JSON = "JSON"
    GEOJSON = "GEOJSON"


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='response_format',
                type=OpenApiTypes.STR,
                enum=[format.value for format in FormatEnum],
                description='Determines the format of the response.',
                required=False,
                default=FormatEnum.JSON.value,
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
class VRIViewSet(GenericViewSet, ListModelMixin):
    """
    ViewSet for the Vector Risk Index (VRI) model.
    """
    queryset = VRI.objects
    serializer_class = VRISerializer

    def get_queryset(self):
        """
        Override the get_queryset method to filter the queryset based on
        the method action and the request parameters.
        """
        queryset = super().get_queryset()

        # Query parameters
        format = self.request.query_params.get('response_format')

        if format == FormatEnum.GEOJSON:
            queryset = queryset.with_geometry().all()
        else:
            queryset = queryset.all()

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
        format = self.request.query_params.get('response_format')

        if format == FormatEnum.GEOJSON:
            # return VRIWithGeometrySerializer
            return GeoVRISerializer
        return super().get_serializer_class()

    # TODO: Query parameters: geometry, level
    # TODO: Depending on the query parameter, return a JSON or a GeoJSON
    # TODO: Get serializer depending on the mixin (list or detail)
    # TODO: 2 actions: history and seasonality
