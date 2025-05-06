

from django.db.models import Max
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

    def get_queryset(self):
        """
        Override the get_queryset method to filter the queryset based on
        the method action and the request parameters.
        """
        queryset = super().get_queryset()

        if self.action == 'list':
            # Get the most recent date in the queryset
            latest_date = queryset.aggregate(latest=Max('date'))['latest']
            if latest_date:
                # Filter the queryset to include only the latest date
                queryset = queryset.filter(date=latest_date)
            else:
                queryset = queryset.none()
        return queryset

    # TODO: Query parameters: geometry, level
    # TODO: Depending on the query parameter, return a JSON or a GeoJSON
    # TODO: Get serializer depending on the mixin (list or detail)
    # TODO: 2 actions: history and seasonality
