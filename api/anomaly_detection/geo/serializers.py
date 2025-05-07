from rest_framework.serializers import ModelSerializer

from anomaly_detection.geo.models import Municipality


class MunicipalitySerializer(ModelSerializer):
    """
    Serializer for the Municipality model.
    """
    class Meta:
        model = Municipality
        fields = ['id', 'code', 'name', 'alt_name', 'province']  # exclude geometry


class MunicipalityWithGeometrySerializer(ModelSerializer):
    """
    Serializer for the Municipality model with geometry.
    """

    class Meta:
        model = Municipality
        fields = ['id', 'code', 'name', 'alt_name', 'province', 'geometry']
