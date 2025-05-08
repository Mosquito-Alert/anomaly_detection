from rest_framework.serializers import ModelSerializer

from anomaly_detection.geo.models import Municipality


class MunicipalitySerializer(ModelSerializer):
    """
    Serializer for the Municipality model.
    """
    class Meta:
        model = Municipality
        fields = ['id', 'code', 'name', 'alt_name', 'province']  # exclude geometry


class MunicipalitySimplifiedSerializer(ModelSerializer):
    """
    Serializer for the Municipality model with only the fundamental fields.
    """
    class Meta:
        model = Municipality
        fields = ['code', 'name']  # exclude geometry
