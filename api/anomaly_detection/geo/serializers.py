

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from anomaly_detection.geo.models import Municipality


class MunicipalitySerializer(ModelSerializer):
    """
    Serializer for the Municipality model.
    """
    province = SerializerMethodField()

    def get_province(self, obj=None) -> str:
        """
        Get the province name from the province related model.
        """
        if obj and obj.province:
            return obj.province.name
        return None

    class Meta:
        model = Municipality
        fields = ['code', 'name', 'alt_name', 'province']
