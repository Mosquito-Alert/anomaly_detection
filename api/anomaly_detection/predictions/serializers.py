from rest_framework.serializers import ModelSerializer
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from anomaly_detection.geo.serializers import MunicipalitySerializer, MunicipalitySimplifiedSerializer

from .models import Metric, MetricSeasonality


class MetricSerializer(ModelSerializer):
    """
    Serializer for the Metrics.
    """
    region = MunicipalitySerializer()

    class Meta:
        model = Metric
        fields = ['id', 'date', 'actual_value', 'predicted_value', 'lower_value', 'upper_value',
                  'trend', 'anomaly_degree', 'region']
        read_only_fields = ['created_at', 'updated_at', 'anomaly_degree']


class GeoMetricSerializer(GeoFeatureModelSerializer):
    """
    Serializer for the Metrics.
    """
    region = MunicipalitySimplifiedSerializer()
    geometry = GeometryField(
        source='region.geometry',
        read_only=True
    )

    class Meta:
        model = Metric
        geo_field = "geometry"  # Use the geometry field from the related region

        fields = ['id', 'anomaly_degree', 'region']
        read_only_fields = ['created_at', 'updated_at', 'anomaly_degree']


class MetricSeasonalitySerializer(ModelSerializer):
    """
    Serializer for the Metric Seasonality model.
    """
    class Meta:
        model = MetricSeasonality
        fields = ['id', 'index', 'yearly_value', 'region']
        read_only_fields = ['created_at', 'updated_at']
