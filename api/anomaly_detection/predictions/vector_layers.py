from django.db import models
from vectortiles import VectorLayer

from .models import Metric


class MetricMunicipalityVectorLayer(VectorLayer):
    # model = Metric
    # TODO: how to pass a query param to the vector layer
    queryset = Metric.objects.with_geometry()
    # .filter(
    #     date=models.Subquery(
    #         Metric.objects.values('date').order_by('-date')[:1]
    #     )
    # )
    id = "metrics"
    tile_fields = ('anomaly_degree',)
    min_zoom = 0
    geom_field = "region__geometry"
