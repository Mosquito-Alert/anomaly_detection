
from datetime import datetime
from celery import shared_task
from django.db import IntegrityError, transaction
from django.utils import timezone


@shared_task
def refresh_prediction_task(metric_id, refresh_progress=True):
    """
    Invokes the predictor and assign the Prediction fields.
    """
    from anomaly_detection.predictions.models import Metric, MetricPredictionProgress, Predictor

    try:
        metric = Metric.objects.get(id=metric_id)
    except Metric.DoesNotExist:
        return

    aware_datetime = timezone.make_aware(
        datetime.combine(metric.date, datetime.min.time())
    )

    if not getattr(metric, 'predictor', None):
        try:
            metric.predictor = Predictor.objects.get_not_expired(region_id=metric.region, date=aware_datetime)
        except Predictor.DoesNotExist:
            try:
                with transaction.atomic():
                    metric.predictor = Predictor.objects.create(
                        region_id=metric.region_id,
                        last_training_date=aware_datetime,
                    )
            except IntegrityError:
                # If the IntegrityError is raised, it means that another process has already created the predictor
                # and we can safely ignore this error.
                metric.predictor = Predictor.objects.get_not_expired(region_id=metric.region, date=aware_datetime)
        finally:
            metric.save(update_fields=['predictor'])

    if result := metric.predictor.predict(date=metric.date, value=metric.value):
        metric.predicted_value = result['yhat']
        metric.upper_value = result['yhat_upper']
        metric.lower_value = result['yhat_lower']
        metric.save()

    if refresh_progress:
        MetricPredictionProgress.refresh(date=metric.date)
