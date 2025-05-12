import uuid
from django.db import models
from django.db.models import Case, F, Value, When

from anomaly_detection.geo.models import Municipality
from anomaly_detection.predictions.managers import RegionSelectedManager


class Metric(models.Model):
    """
    Model to store a metric of data, such as a Bites Index.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # TODO: Use ContentType and GenericRelation for region field
    region = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='metrics',
        unique_for_date='date'
    )
    # TODO: type. A foreign key to a model MetricType

    date = models.DateField()
    value = models.FloatField()
    predicted_value = models.FloatField()
    lower_value = models.FloatField()
    upper_value = models.FloatField()
    trend = models.FloatField()

    anomaly_degree = models.GeneratedField(
        expression=Case(
            When(value__gt=F('upper_value'),
                 then=(F('value') - F('upper_value')) / F('value')),
            When(value__lt=F('lower_value'),
                 then=(F('value') - F('lower_value')) / F('value')),
            default=Value(0.0),
            output_field=models.FloatField(),
        ),
        output_field=models.FloatField(),
        # If db_persist is set to false, then the field will not be persisted in the database
        # and the computed value will be calculated on the READ queries, which is not optimal.
        db_persist=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RegionSelectedManager()

    def __str__(self):
        return f"Bites Index Metric for {self.region.name} on {self.date}: {self.value}"

    class Meta:
        ordering = ['region', '-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['region', 'date'])
        ]
        unique_together = ('region', 'date',)
        verbose_name = 'Metric'
        verbose_name_plural = 'Metrics'


class MetricSeasonality(models.Model):
    """
    Model to store the seasonality data for a specific Metric.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
        return f"Bites Index Metric Seasonality for {self.region.name} on day {self.index+1}: {self.yearly_value}"

    class Meta:
        ordering = ['region', 'index']
        indexes = [
            models.Index(fields=['index']),
        ]
        verbose_name = 'Seasonality for metric'
        verbose_name_plural = 'Seasonalities for metric'


class MetricExecution(models.Model):
    """
    Model to store the data prediction execution information.
    Every time the metrics are updated, a prediction will be executed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    # Percentage of values successfully predicted and saved.
    success_percentage = models.FloatField()

    def __str__(self):
        return f"Metric Execution of the day {self.date} with result: {self.success_percentage}"

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['-date'])
        ]
        verbose_name = "Metric Execution"
        verbose_name_plural = "Metric Executions"
