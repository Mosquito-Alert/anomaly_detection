

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

    def to_representation(self, instance):
        """
        Override to_representation to include the province name.
        """
        res = super().to_representation(instance)
        if not self.context.get('geometry', False):
            res['geometry'] = None
        return res

    class Meta:
        model = Municipality
        fields = ['id', 'code', 'name', 'alt_name', 'province', 'geometry']
        extra_kwargs = {
            'geometry': {'allow_null': True}
        }
