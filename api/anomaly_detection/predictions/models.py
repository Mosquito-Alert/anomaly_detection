import uuid
from datetime import datetime
from typing import Optional, TypedDict
import pandas as pd

from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.db.models import Case, F, Value, When
from django.utils.translation import gettext_lazy as _
from prophet import Prophet
from prophet.plot import seasonality_plot_df
from prophet.serialize import model_to_json as prophet_model_to_json
from rest_framework.fields import MaxValueValidator, MinValueValidator


from anomaly_detection.geo.models import Municipality
from anomaly_detection.predictions.managers import PredictorManager, RegionSelectedManager


class PredictionResult(TypedDict):
    yhat: float
    yhat_upper: float
    yhat_lower: float


class Predictor(models.Model):
    """
    Model to store the predictor model and the prediction results.
    """
    EXPIRY_DAYS = 30
    MIN_DAYS_FOR_TRAINING = 60

    region = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='predictors',
        verbose_name=_('Region'),
        help_text=_('The region associated to the predictor.')
    )
    last_training_date = models.DateTimeField(
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
    # ! CAREFUL: The type ArrayField only works in PostgreSQL
    yearly_seasonality = ArrayField(
        base_field=models.FloatField(),
        size=365,
        null=True,
        blank=True,
        verbose_name=_('Seasonality'),
        help_text=_('The predicted seasonality for the metric.')
    )
    trend = ArrayField(
        base_field=models.FloatField(),
        null=True,
        blank=True,
        verbose_name=_('Trend'),
        help_text=_('The predicted serial tendency for the metric.')
    )

    objects = PredictorManager()

    @property
    def is_trained(self) -> bool:
        """
        Whether the predictor is trained or not.
        """
        return self.weights is not None

    #   @celery.task(singleton)
    def predict(self, date: datetime, value: float) -> Optional[PredictionResult]:
        """
        Predicts the values for the specified data.
        """
        from prophet.serialize import model_from_json
        if not self.is_trained:
            self.train()
        if not self.is_trained:
            # This second comprobation is needed for the first iterations (first 30 days)
            return

        prophet = model_from_json(self.weights)

        df = pd.DataFrame([(date, value)], columns=['ds', 'y'])
        df['cap'] = 1
        df['floor'] = 0
        try:
            forecast: PredictionResult = prophet.predict(df).iloc[0]
        except Exception as e:
            raise Exception(f"Error predicting the values: {str(e)}")
        return forecast

#   @celery.task(singleton)
    def train(self, force: bool = False) -> None:
        """
        Trains the predictor model with past data.
        """
        if self.is_trained and not force:
            return

        # NOTE: Do not delete the order by date, as it is needed for the Prophet model.
        metric_qs = Metric.objects.filter(date__lt=self.last_training_date, region=self.region).order_by('date')

        df = pd.DataFrame.from_records(
            ({'ds': obj.date, 'y': obj.value} for obj in metric_qs.iterator())  # Generator
        )
        # TODO: Apply Savitzky-Golay filter with safeguards. Maybe, create a new field in Metric (smoothed_value)

        if (df['y'].isna()).all() or (df['y'].eq(0)).all():
            return

        first_non_zero = df[df["y"] != 0].iloc[0]
        df_first_zeros = df[(df['y'] == 0) & (df['ds'] < first_non_zero['ds'])]['ds'].reset_index()
        df_first_zeros['holiday'] = 'no-prediction-yet'

        if (len(df) - len(df_first_zeros)) <= self.MIN_DAYS_FOR_TRAINING:
            # If there are not enough quality data to train the model, do not train it.
            return

        try:
            # We take advantage of the holidays feature of the Prophet model to avoid training with no quality data.
            model = Prophet(
                growth='logistic',
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                holidays=df_first_zeros[['ds', 'holiday']] if df_first_zeros else None,
            )
        except Exception as e:
            raise Exception(f"Error creating the Prophet model: {str(e)}")
        # Logistic growth and boundaries between 0 and 1 are specifict to the bite risk model, which value is a
        # probability. If ever needs to use other kind of metric set the boundaries on the MetricType model.
        df.loc[:, 'cap'] = 1
        df.loc[:, 'floor'] = 0
        model.fit(df)

        # Trend
        future = model.make_future_dataframe(periods=0)
        future['cap'] = 1  # Ensure the future data has the cap
        future['floor'] = 0  # Ensure the future data has the floor
        forecast = model.predict(future)

        # Seasonality
        df_w = seasonality_plot_df(m=model, ds=pd.date_range(start='2017-01-01', periods=365))
        seas_df = model.predict_seasonal_components(df_w)

        # Save
        self.weights = prophet_model_to_json(model)
        self.trend = forecast['trend'].to_list()
        self.yearly_seasonality = seas_df['yearly'].reset_index().to_list()
        self.save()

    def __str__(self):
        return f"Predictor for the region {self.region.name} for the model predicted in {self.last_training_date}"

    class Meta:
        ordering = ['region', '-last_training_date']
        indexes = [
            models.Index(fields=['region', 'last_training_date'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['region', 'last_training_date'], name='unique_predictor'
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
        null=False,
        blank=False,
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
        verbose_name=_('Upper value'),
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

    def refresh_prediction(self):
        """
        Invokes the predictor and assign the Prediction fields.
        """
        try:
            result: PredictionResult = self.predictor.predict(data=(self.date, self.value))
            self.predicted_value = result.yhat
            self.upper_value = result.yhat_upper
            self.lower_value = result.yhat_lower
            self.save()
        except Exception as e:
            raise Exception(f"Error during prediction: {str(e)}")

        # CHECK: For race conditions
        MetricPredictionProgress.refresh(date=self.date)

    def save(self, *args, **kwargs):
        is_adding = self._state.adding  # A new object is being created

        if not self.predictor:
            try:
                self.predictor = Predictor.objects.get_not_expired(region_id=self.region, date=self.date)
            except Predictor.DoesNotExist:
                self.predictor = Predictor.objects.create(
                    region_id=self.region_id,
                    last_training_date=self.date
                )

        # Save the initial Metric with the prediction values and the predictor to None.
        super().save(*args, **kwargs)

        # Assign a preditor to the Metric and set the prediction values.
        if is_adding:
            self.refresh_prediction()

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


class MetricPredictionProgress(models.Model):
    """
    Model to store the data prediction progress information.
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
        default=0,
        verbose_name=_('Success percentage'),
        help_text=_('The percentage of success of the execution.'),
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )

    @classmethod
    def refresh(cls, date: datetime):
        with transaction.atomic():
            metrics_qs = Metric.objects.select_for_update().filter(date=date)
            total = metrics_qs.count()
            # total_finished = metrics_qs.predicted()
            total_finished = metrics_qs.filter(predicted_value__isnull=False).count()

            perc = 0
            if total > 0:
                perc = total_finished / total

            cls.objects.update_or_create(date=date, defaults={'success_percentage': perc})

    def __str__(self):
        return f"Metric Execution of the day {self.date} with result: {self.success_percentage}"

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['-date'])
        ]
        verbose_name = "Metric Execution"
        verbose_name_plural = "Metric Executions"
