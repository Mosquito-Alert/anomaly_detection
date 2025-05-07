from rest_framework.serializers import ModelSerializer

from anomaly_detection.geo.serializers import MunicipalitySerializer, MunicipalityWithGeometrySerializer

from .models import VRI, VRISeasonality


class VRISerializer(ModelSerializer):
    """
    Serializer for the Vector Risk Index model.
    """
    region = MunicipalitySerializer()

    class Meta:
        model = VRI
        # TODO: Explicity set the fields to be included in the serializer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'anomaly_degree']


class VRIWithGeometrySerializer(VRISerializer):
    """
    Serializer for the Vector Risk Index model.
    """
    region = MunicipalityWithGeometrySerializer()


class VRISeasonalitySerializer(ModelSerializer):
    """
    Serializer for the VRI Seasonality model.
    """
    class Meta:
        model = VRISeasonality
        # TODO: Explicity set the fields to be included in the serializer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
