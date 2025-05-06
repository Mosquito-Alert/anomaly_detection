"""
Django command to insert VRI data into the database.

This command reads VRI data from CSV files, processes it, and inserts it into the database.
It handles the VRI data and the seasonality data.
"""
import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from anomaly_detection.vri.models import VRI, VRISeasonality
from anomaly_detection.geo.models import Municipality


class Command(BaseCommand):
    """
    Django command to insert VRI data into the database.
    """

    help = """Load VRI data into the database."""

    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

    def add_arguments(self, parser):
        parser.add_argument(
            '--input-vri',
            type=str,
            default=os.path.join(self.DATA_DIR, 'bites_test.csv'),
            help='Path to the input VRI CSV file'
        )
        parser.add_argument(
            '--input-seasonality',
            type=str,
            default=os.path.join(self.DATA_DIR, 'bites_seasonality_test.csv'),
            help='Path to the input VRI seasonality CSV file'
        )

    def process_vri_data(self, vri_data):
        # Rename columns to match the model fields
        vri_data.rename(columns={
            'ds': 'date',
            'y': 'actual_value',
            'yhat': 'predicted_value',
            'yhat_lower': 'lower_value',
            'yhat_upper': 'upper_value',
        }, inplace=True)
        # Convert date column to datetime
        vri_data['date'] = pd.to_datetime(vri_data['date'])
        # Conver all numeric columns to float
        vri_data['actual_value'] = vri_data['actual_value'].astype(float)
        vri_data['predicted_value'] = vri_data['predicted_value'].astype(float)
        vri_data['lower_value'] = vri_data['lower_value'].astype(float)
        vri_data['upper_value'] = vri_data['upper_value'].astype(float)
        vri_data['trend'] = vri_data['trend'].astype(float)
        # Convert code to string and upper case
        vri_data['code'] = vri_data['code'].astype(str).str.upper()
        return vri_data

    def process_seasonality_data(self, seasonality_data):
        # Rename columns to match the model fields
        # index,yearly,code
        seasonality_data.rename(columns={'yearly': 'yearly_value', }, inplace=True)
        # Convert index to int
        seasonality_data['index'] = seasonality_data['index'].astype(int)
        # Convert yearly_value to float
        seasonality_data['yearly_value'] = seasonality_data['yearly_value'].astype(float)
        # Convert code to string and upper case
        seasonality_data['code'] = seasonality_data['code'].astype(str).str.upper()
        return seasonality_data

    def insert_vri_data(self, vri_data):
        """Insert VRI data into the database"""
        with transaction.atomic():
            for _, row in vri_data.iterrows():
                try:
                    # Get the municipality object
                    municipality = Municipality.objects.get(code=row['code'])
                    # Create or update the VRI object
                    VRI.objects.update_or_create(
                        region=municipality,
                        date=row['date'],
                        actual_value=row['actual_value'],
                        predicted_value=row['predicted_value'],
                        lower_value=row['lower_value'],
                        upper_value=row['upper_value'],
                        trend=row['trend'],
                    )
                except Municipality.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"Municipality with code {row['code']} does not exist."))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error inserting VRI data: {e}"))
            self.stdout.write(self.style.SUCCESS(f"Successfully inserted {len(vri_data)} VRI records.\n"))

    def insert_seasonality_data(self, seasonality_data):
        """Insert seasonality data into the database"""
        with transaction.atomic():
            for _, row in seasonality_data.iterrows():
                try:
                    # Get the municipality object
                    municipality = Municipality.objects.get(code=row['code'])
                    # Create or update the VRISeasonality object
                    VRISeasonality.objects.update_or_create(
                        region=municipality,
                        index=row['index'],
                        yearly_value=row['yearly_value'],
                    )
                except Municipality.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"Municipality with code {row['code']} does not exist."))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error inserting seasonality data: {e}"))
            self.stdout.write(self.style.SUCCESS(
                f"Successfully inserted {len(seasonality_data)} seasonality records.\n"))
        self.stdout.write(self.style.SUCCESS("VRI and seasonality data insertion completed."))

    def handle(self, *args, **options):
        """
        Handle the command to insert VRI data into the database.
        """
        input_vri = options['input_vri']
        input_seasonality = options['input_seasonality']

        # Load VRI data
        vri_data = pd.read_csv(input_vri)
        seasonality_data = pd.read_csv(input_seasonality)
        self.stdout.write(f"Loaded {len(vri_data)} VRI records and {len(seasonality_data)} seasonality records.\n")

        # Process VRI data
        vri_data = self.process_vri_data(vri_data)
        seasonality_data = self.process_seasonality_data(seasonality_data)
        self.stdout.write(f"Processed {len(vri_data)} VRI records and {len(seasonality_data)} seasonality records.\n")

        # Insert VRI data into the database
        self.insert_vri_data(vri_data)
        # Insert seasonality data into the database
        self.insert_seasonality_data(seasonality_data)
