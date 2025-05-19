
from datetime import datetime
from celery import shared_task
from django.utils import timezone


@shared_task
def refresh_prediction_task(metric_id):
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
    # CHECK: The getattr(metric, 'predictor', None) if the create is invoked with a predictor
    # CHECK: Same with predictor_id
    if not getattr(metric, 'predictor', None):
        try:
            metric.predictor = Predictor.objects.get_not_expired(region_id=metric.region, date=aware_datetime)
        except Predictor.DoesNotExist:
            metric.predictor = Predictor.objects.create(
                region_id=metric.region_id,
                last_training_date=aware_datetime,
            )
        finally:
            metric.save(update_fields=['predictor'])

    # Convert timezone-aware datetime to naive datetime for Prophet
    naive_datetime = timezone.make_naive(aware_datetime)

    if result := metric.predictor.predict(date=naive_datetime, value=metric.value):
        metric.predicted_value = result['yhat']
        metric.upper_value = result['yhat_upper']
        metric.lower_value = result['yhat_lower']
        metric.save()

    # CHECK: For race conditions
    MetricPredictionProgress.refresh(date=metric.date)
