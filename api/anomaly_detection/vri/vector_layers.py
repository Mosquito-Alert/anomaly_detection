from django.db import models
from vectortiles import VectorLayer

from .models import VRI


class VRIMunicipalityVectorLayer(VectorLayer):
    # model = VRI
    queryset = VRI.objects.with_geometry().filter(
        date=models.Subquery(
            VRI.objects.values('date').order_by('-date')[:1]
        )
    )
    id = "vris"
    tile_fields = ('anomaly_degree',)
    min_zoom = 0
    geom_field = "region__geometry"
