from rest_framework.serializers import ModelSerializer

from .models import VRI, VRISeasonality


class VRISerializer(ModelSerializer):
    """
    Serializer for the Vector Risk Index model.
    """
    class Meta:
        model = VRI
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_anomaly', 'importance']


class VRISeasonalitySerializer(ModelSerializer):
    """
    Serializer for the VRI Seasonality model.
    """
    class Meta:
        model = VRISeasonality
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
