from rest_framework import serializers
from rest_framework.serializers import (ModelSerializer, Serializer,
                                        SerializerMethodField)

from anomaly_detection.geo.serializers import MunicipalitySerializer

from .models import Metric, Predictor


class MetricSerializer(ModelSerializer):
    """
    Serializer for the Metrics.
    """
    region_code = SerializerMethodField()
    trend = SerializerMethodField()

    def get_region_code(self, obj=None) -> str:
        return obj.region.code

    def get_trend(self, obj=None) -> str:
        return obj.prediction.trend

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
    Serializer for the Metric Seasonality associated to the Predictor model.
    """
    class Meta:
        model = Predictor
        fields = ['seasonality']


class LastMetricDateSerializer(Serializer):
    """
    Serializer for the Metric Executions.
    """
    date = serializers.DateField()


class MetricFileSerializer(Serializer):
    """
    Serializer for uploading a file with a batch of metrics.
    """
    file = serializers.FileField()

    # TODO: def create(): override ...
    # open csv,
    # load it with pandas,
    # order_by
    # def validate_file
    # for loop,
    # Metric.objects.create()

    # transaction for the first step (no prophet)

    class Meta:
        fields = ['file']
