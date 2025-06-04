from django.core.management.base import BaseCommand
from datetime import datetime, timedelta

from django.db import models
from tqdm import tqdm

from anomaly_detection.predictions.models import Metric, Predictor


def generate_date_range(start_str, end_str, fmt='%Y-%m-%d'):
    """
    Generate dates between start_str and end_str (inclusive).

    Args:
        start_str (str): The start date as a string.
        end_str (str): The end date as a string.
        fmt (str): The date format (default '%Y-%m-%d').

    Yields:
        datetime.date: The dates in the range.
    """
    start_date = datetime.strptime(start_str, fmt).date()
    end_date = datetime.strptime(end_str, fmt).date()

    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)


class Command(BaseCommand):
    """
    Django command to update the predicted values in the Metric model, given their assigned predictor.
    """

    help = """Load metrics data into the database."""

    def add_arguments(self, parser):
        parser.add_argument(
            '--region',
            type=str,
            default=None,
            help='Filter by region (e.g., "ESP.1.1.1.1_1")'
        )
        parser.add_argument(
            '--from-date',
            type=str,
            default="2000-01-01",
            help='Start date for filtering metrics (format: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--to-date',
            type=str,
            default="2100-01-01",
            help='End date for filtering metrics (format: YYYY-MM-DD)'
        )

    def handle(self, *args, **options):
        """
        Handle the command to insert predictions data into the database.
        """

        from_date = options.get('from_date')
        to_date = options.get('to_date')
        region = options.get('region')

        metric_to_update = []
        predictor_qs = Predictor.objects.filter(
            models.Exists(
                Metric.objects.filter(
                    predictor=models.OuterRef('pk'),
                    date__gte=from_date,
                    date__lte=to_date
                )
            )
        )
        if region:
            predictor_qs = predictor_qs.filter(region__code=region)

        for predictor in tqdm(predictor_qs.iterator(chunk_size=1000), total=predictor_qs.count()):
            date_to_pk = {
                metric.date: metric
                for metric in predictor.metrics.filter(date__gte=from_date, date__lte=to_date).iterator(chunk_size=1000)
            }

            for result in predictor.predict(dates=list(generate_date_range(from_date, to_date))):
                if metric := date_to_pk.get(result['datetime'].date(), None):
                    metric.predicted_value = result['yhat']
                    metric.upper_value = result['yhat_upper']
                    metric.lower_value = result['yhat_lower']
                    metric_to_update.append(metric)

            Metric.objects.bulk_update(
                metric_to_update,
                batch_size=2000,
                fields=['predicted_value', 'upper_value', 'lower_value']
            )
