import uuid
from datetime import datetime
from typing import TypedDict
import pandas as pd

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Case, F, Value, When
from django.utils.translation import gettext_lazy as _


from anomaly_detection.geo.models import Municipality
from anomaly_detection.predictions.managers import RegionSelectedManager


class PredictionResult(TypedDict):
    predicted_value: float
    upper_value: float
    lower_value: float


class Predictor(models.Model):
    """
    Model to store the predictor model and the prediction results.
    """
    region = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='predictors',
        verbose_name=_('Region'),
        help_text=_('The region associated to the predictor.')
    )
    trained_at = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name=_('Trained at'),
        help_text=_('The specified date in which the model was trained.')
    )
    weights = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('Weights'),
        help_text=_('The predictor model itself.')
    )
    seasonality = ArrayField(
        base_field=models.FloatField(),
        size=365,
        null=True,
        blank=True,
        verbose_name=_('Seasonality'),
        help_text=_('The predicted seasonality for the metric.')
    )  # TODO: What if I have another database?
    trend = ArrayField(
        base_field=models.FloatField(),
        null=True,
        blank=True,
        verbose_name=_('Trend'),
        help_text=_('The predicted serial tendency for the metric.')
    )

    @property
    def is_trained(self) -> bool:
        """
        Whether the predictor is trained or not.
        """
        return self.weights is not None

    # @classmethod
    # def predict(cls, region, value) -> PredictionResult:
    #     """
    #     ??????????????
    #     """
    #     Predictor.get_preodfa(region, date).predict(date, value)
    #     obj = cls.objects.filter(

    #     )
    #     #   prophet = ProphetModel.objects.filter(region_id=self.region_id, train_date__lte=self.date, train_date__gte=(self.date - timedelta(months=1))).order_by('-trained_date').first()
    #     #   if not prophet:
    #     #       prophet = ProphetModel.objects.create(region_id=region, train_date=self.date)
    #     #

        #   @celery.task
    def predict(self, date: datetime, value: float) -> PredictionResult:
        """
        Predicts the values for the specified data.
        """
        from prophet.serialize import model_from_json
        if not self.is_trained:
            self.train()
        prophet = model_from_json(self.weights)

        df = pd.DataFrame(tuple(date, value), columns=['ds', 'y'])
        df['cap'] = 1
        df['floor'] = 0
        forecast = prophet.predict(df).iloc[0]
        return PredictionResult(
            predicted_value=forecast['yhat'],
            upper_value=forecast['yhat_upper'],
            lower_value=forecast['yhat_lower']
        )

    def train(self, force: bool = False) -> None:
        """
        Trains the predictor model with past data.
        """
        if self.is_trained and not force:
            return

        metrics = Metric.objects.filter(date__lte=self.trained_at, region=self.region)
        pass

#   @celery.task(singleton)
#   def train(self, force: bool = False, commit: bool = False):
#       if self.weights and not force:
#           return
#
#       prophet_library.train(before_date=self.trained_at)
#       self.weights = prophet_library.save(format='json')
#       if commit:
#           self.save(update_fields=['weights'])

    def __str__(self):
        return f"Predictor for the region {self.region.name} for the model predicted in {self.trained_at}"

    class Meta:
        ordering = ['region', '-trained_at']
        indexes = [
            models.Index(fields=['region', 'trained_at'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['region', 'trained_at'], name='unique_predictor'
            )
        ]
        verbose_name = 'Predictor'
        verbose_name_plural = 'Predictors'


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
    predictor = models.ForeignKey(
        Predictor,
        on_delete=models.RESTRICT,
        related_name="metrics",
        null=True,  # ! CHECK: If this is possible
        blank=True,
        verbose_name=_('Predictor'),
        help_text=_('The predictor which has the model and the predicted values associaded to the metric.')
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

    # TODO: override save
    # change "predict" to a more fitting name (refresh_prediction, estimate, etc.)

    def predict(self):
        result: PredictionResult = Predictor.predict(data=(self.date, self.value))
        self.upper_value = result.upper_value
        self.save()

    # @celery.task
    # def predict(self) --> prophet y update
    #   prophet = ProphetModel.objects.filter(region_id=self.region_id, train_date__lte=self.date, train_date__gte=(self.date - timedelta(months=1))).order_by('-trained_date').first()
    #   if not prophet:
    #       prophet = ProphetModel.objects.create(region_id=region, train_date=self.date)
    #
    #   predictions = await prophet.predict()
    #   self.fields____ = predictions.y_hat
    #   self.save()

    # def save(self, *args, **kwargs):
    #   is_adding = self._state.adding
    #
    #   super().save(*args, **kwargs)
    #
    #   if is_adding:
    #       self.predict()
    #   MetricExecution.objects.get(date=self.date).refresh()

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

    # def refresh(self):
    #     qs = Metric.objects.filter(date=self.date)
    #     total = qs.count()
    #     total_finished = qs.filter(upper_bound__isnull=False).count()

    #     self.success_percentage = total_finished/total
    #     self.save(update_fields=['success_percentage'])

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['-date'])
        ]
        verbose_name = "Metric Execution"
        verbose_name_plural = "Metric Executions"
