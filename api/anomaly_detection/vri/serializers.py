from rest_framework.serializers import ModelSerializer
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from anomaly_detection.geo.serializers import MunicipalitySerializer, MunicipalitySimplifiedSerializer

from .models import VRI, VRISeasonality


class VRISerializer(ModelSerializer):
    """
    Serializer for the Vector Risk Index model.
    """
    region = MunicipalitySerializer()

    class Meta:
        model = VRI
        fields = ['id', 'date', 'actual_value', 'predicted_value', 'lower_value', 'upper_value',
                  'trend', 'anomaly_degree', 'region']
        read_only_fields = ['created_at', 'updated_at', 'anomaly_degree']


class GeoVRISerializer(GeoFeatureModelSerializer):
    """
    Serializer for the Vector Risk Index model.
    """
    region = MunicipalitySimplifiedSerializer()
    geometry = GeometryField(
        source='region.geometry',
        read_only=True
    )

    class Meta:
        model = VRI
        geo_field = "geometry"  # Use the geometry field from the related region

        fields = ['id', 'anomaly_degree', 'region']
        read_only_fields = ['created_at', 'updated_at', 'anomaly_degree']


class VRISeasonalitySerializer(ModelSerializer):
    """
    Serializer for the VRI Seasonality model.
    """
    class Meta:
        model = VRISeasonality
        fields = ['id', 'index', 'yearly_value', 'region']
        read_only_fields = ['created_at', 'updated_at']
