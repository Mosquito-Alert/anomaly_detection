

from rest_framework.serializers import ModelSerializer

from anomaly_detection.geo.models import Municipality


class MunicipalitySerializer(ModelSerializer):
    """
    Serializer for the Municipality model.
    """

    class Meta:
        model = Municipality
        fields = ['code', 'name', 'alt_name']
