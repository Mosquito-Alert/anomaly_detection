from django.db import models

from anomaly_detection.geo.models import Municipality
from anomaly_detection.vri.managers import RegionSelectedManager


class VRI(models.Model):
    """
    Model to store the Vector Risk Index data.
    """
    # TODO: Use ContentType and GenericRelation for region field
    region = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='historical_vri',
        unique_for_date='date'
    )

    date = models.DateField()
    actual_value = models.FloatField()
    predicted_value = models.FloatField()
    lower_value = models.FloatField()
    upper_value = models.FloatField()
    trend = models.FloatField()
    # TODO: These two fields should be determined with the previous values: GeneratedField
    is_anomaly = models.BooleanField(default=False)
    importance = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RegionSelectedManager()

    def __str__(self):
        return f"VRI for {self.region.name} on {self.date}: {self.actual_value}"

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['region', 'date'])
        ]
        unique_together = ('region', 'date',)
        verbose_name = 'Vector Risk Index'
        verbose_name_plural = 'Vector Risk Indexes'


class VRISeasonality(models.Model):
    """
    Model to store the seasonality data for the Vector Risk Index.
    """
    region = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='seasonalities',
        # unique_for_date='date'
    )
    # date = models.DateField()
    index = models.SmallIntegerField()
    yearly_value = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RegionSelectedManager()

    def __str__(self):
        return f"VRI Seasonality for {self.region.name} on day {self.index+1}: {self.yearly_value}"

    class Meta:
        ordering = ['index']
        indexes = [
            models.Index(fields=['index']),
        ]
        verbose_name = 'VRI Seasonality'
        verbose_name_plural = 'VRI Seasonalities'
