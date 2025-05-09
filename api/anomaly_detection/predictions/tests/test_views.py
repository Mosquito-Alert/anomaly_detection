

import pytest
from django.urls import reverse
from rest_framework import status

from anomaly_detection.predictions.models import Metric
from anomaly_detection.predictions.serializers import (MetricSerializer,
                                                       GeoMetricSerializer)

Metrics_URL = reverse('metrics:metrics-list')


@pytest.mark.django_db()
class TestMetricListView:
    """
    Tests the Metric View for the List action.
    """

    def _get_queries(self, connection):
        """
        Filter the queries to get only the ones that contain 'SELECT' and 'metric'.
        """
        return [
            query for query in connection.queries
            if 'SELECT' in query['sql']
            and 'metric' in query['sql']
            and not query['sql'].startswith('EXPLAIN')
            and 'silk' not in query['sql']
        ]

    def test_retrieve_metric_list(self, metrics, client):
        """
        Retrieve the list of Metric instances.
        """
        res = client.get(Metrics_URL)

        metrics_from_db = Metric.objects.all().filter(date=metrics[3].date)
        serialized = MetricSerializer(metrics_from_db, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 2
        assert res.data[1]['actual_value'] == metrics[3].actual_value
        assert res.data == serialized.data
        # Check that the region is not serialized with geometry
        assert res.data[1]['region'].get('geometry') is None

    def test_retrieve_metric_list_number_of_queries(self, metrics, client, connection):
        """
        Retrieve the list of Metric instances and check the number of queries executed.
        """

        res = client.get(Metrics_URL)

        assert res.status_code == status.HTTP_200_OK
        # Check that only 2 queries are executed (1 for getting the latest date
        # and 1 for getting the Metric instances with the region joined)
        _ = res.data[1]['actual_value']
        _ = res.data[1]['region']['name']
        assert len(self._get_queries(connection)) == 2

# TODO: Protobuffer
    # def test_retrieve_metric_list_with_geometry(self, metrics, client):
    #     """
    #     Retrieve the list of Metric instances with geometry.
    #     """
    #     res = client.get(Metrics_URL, {'response_format': 'GEOJSON'})

    #     metrics_from_db = Metric.objects.with_geometry().all().filter(date=metrics[3].date)
    #     serialized = GeoMetricSerializer(metrics_from_db, many=True)

    #     assert res.status_code == status.HTTP_200_OK

    #     # Check that the response is in GEOJSON format
    #     assert 'features' in res.data

    #     # Check the data
    #     res_data = res.data['features']
    #     assert len(res_data) == 2
    #     assert res_data[1]['properties']['anomaly_degree'] == metrics[3].anomaly_degree
    #     assert res_data[1]['properties']['region']['code'] == metrics[3].region.code

    #     # Check that the region is not serialized with geometry or other optional fields
    #     assert res_data[1]['properties']['region'].get('geometry') is None
    #     assert res_data[1]['properties']['region'].get('alt_name') is None

    #     # Check the geometry
    #     assert 'geometry' in res_data[1]
    #     assert res_data[1]['geometry']['type'] == 'MultiPolygon'
    #     assert res_data[1]['geometry']['coordinates'] is not None  # TODO: Maybe check the coordinates

    #     # Final check with the serialized data
    #     assert res.data == serialized.data

    # def test_retrieve_metric_list_with_geometry_number_of_queries(self, metrics, client, connection):
    #     """
    #     Retrieve the list of Metric instances with geometry and check the number of queries executed
    #     """
    #     res = client.get(Metrics_URL, {'response_format': 'GEOJSON'})

    #     assert res.status_code == status.HTTP_200_OK
    #     # Check that only 2 queries are executed (1 for getting the latest date
    #     # and 1 for getting the Metric instances with the region joined)
    #     _ = res.data['features'][1]['properties']['anomaly_degree']
    #     _ = res.data['features'][1]['properties']['region']['code']
    #     _ = res.data['features'][1]['geometry']
    #     assert len(self._get_queries(connection)) == 2
