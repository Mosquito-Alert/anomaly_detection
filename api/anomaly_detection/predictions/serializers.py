from rest_framework import serializers
from rest_framework.serializers import (ModelSerializer, Serializer,
                                        SerializerMethodField)

from anomaly_detection.geo.serializers import MunicipalitySerializer

from .models import Metric, MetricSeasonality


class MetricSerializer(ModelSerializer):
    """
    Serializer for the Metrics.
    """
    region_code = SerializerMethodField()

    def get_region_code(self, obj=None) -> str:
        return obj.region.code

    class Meta:
        model = Metric
        fields = ['id', 'date', 'value', 'predicted_value', 'lower_value', 'upper_value',
                  'trend', 'anomaly_degree', 'region_code']
        read_only_fields = ['created_at', 'updated_at', 'anomaly_degree']


class MetricDetailSerializer(MetricSerializer):
    """
    Serializer for the Metric detail.
    """
    region = MunicipalitySerializer()

    class Meta(MetricSerializer.Meta):
        fields = ['id', 'date', 'value', 'predicted_value', 'lower_value', 'upper_value',
                  'trend', 'anomaly_degree', 'region']


class MetricSeasonalitySerializer(ModelSerializer):
    """
    Serializer for the Metric Seasonality model.
    """
    class Meta:
        model = MetricSeasonality
        fields = ['id', 'index', 'yearly_value']
        read_only_fields = ['created_at', 'updated_at']


class LastMetricDateSerializer(Serializer):
    """
    Serializer for the Metric Executions.
    """
    date = serializers.DateField()
