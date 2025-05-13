import uuid
from django.db import models
from django.db.models import Case, F, Value, When
from django.utils.translation import gettext_lazy as _

from anomaly_detection.geo.models import Municipality
from anomaly_detection.predictions.managers import RegionSelectedManager


class Metric(models.Model):
    """
    Model to store a metric of data, such as a Bites Index.
    """
    # TODO: Change the name to uuid
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # TODO: Use ContentType and GenericRelation for region field
    region = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='metrics',
        verbose_name=_('Region'),
        help_text=_('The region associated to the metric.')
    )
    # TODO: type. A foreign key to a model MetricType

    date = models.DateField(
        null=False,
        blank=False,
        verbose_name=_('Date'),
        help_text=_('The date of the metric.')
    )
    value = models.FloatField(
        null=False,
        blank=False,
        verbose_name=_('Value'),
        help_text=_('The actual value of the metric.')
    )
    predicted_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Predicted value'),
        help_text=_('The predicted value of the metric. This value will be estimated at creation.'),
    )
    lower_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Lower value'),
        help_text=_('The predicted lower band value of the metric, from which values will be \
            considerated as anomalies. This value will be estimated at creation.')
    )
    upper_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Lower value'),
        help_text=_('The predicted upper band value of the metric, from which values will be \
            considerated as anomalies. This value will be estimated at creation.')
    )
    trend = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Trend'),
        help_text=_('The predicted serial tendency for the metric. This value will be estimated at creation.')
    )

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
        blank=True,
        null=True,
        verbose_name=_('Anomaly degree'),
        help_text=_('The degree of the anomaly, a range of values that starts on -1 (a lower anomaly of the \
            highest degree) and ends on +1 (a upper anomaly of the highest degree). The 0 value means that \
            these is no anomaly. This value will be estimated at creation.')
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
        constraints = [
            models.UniqueConstraint(
                fields=['region', 'date'], name='unique_metric'
            )
        ]
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
        verbose_name=_('Region'),
        help_text=_('The region associated to the seasonality.')
    )
    index = models.SmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Index'),
        help_text=_('The index position of the seasonality for a list of the days of a year. This translates to \
            the day number minus 1; values from 0 to 364 (or 365 for the leap years).')
    )
    yearly_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Yearly value'),
        help_text=_('The value of the seasonality prediction for a certain day.')
    )

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
        constraints = [
            models.UniqueConstraint(
                fields=['region', 'index'], name='unique_region_seasonality'
            )
        ]
        verbose_name = 'Seasonality for metric'
        verbose_name_plural = 'Seasonalities for metric'


class MetricExecution(models.Model):
    """
    Model to store the data prediction execution information.
    Every time the metrics are updated, a prediction will be executed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(
        unique=True,
        null=False,
        blank=False,
        verbose_name=_('Date'),
        help_text=_('The date of the execution.')
    )
    # Percentage of values successfully predicted and saved.
    success_percentage = models.FloatField(
        null=False,
        blank=False,
        verbose_name=_('Success percentage'),
        help_text=_('The percentage of success of the execution.')
    )

    def __str__(self):
        return f"Metric Execution of the day {self.date} with result: {self.success_percentage}"

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['-date'])
        ]
        verbose_name = "Metric Execution"
        verbose_name_plural = "Metric Executions"
