

import pytest
from django.urls import reverse
from rest_framework import status

from anomaly_detection.vri.models import VRI
from anomaly_detection.vri.serializers import (VRISerializer,
                                               VRIWithGeometrySerializer)

VRI_URL = reverse('vri:vri-list')


@pytest.mark.django_db()
class TestVRIListView:
    """
    Tests the VRI View for the List action.
    """

    def _get_queries(self, connection):
        """
        Filter the queries to get only the ones that contain 'SELECT' and 'vri'.
        """
        return [
            query for query in connection.queries
            if 'SELECT' in query['sql']
            and 'vri' in query['sql']
            and not query['sql'].startswith('EXPLAIN')
            and 'silk' not in query['sql']
        ]

    def test_retrieve_vri_list(self, vris, client):
        """
        Retrieve the list of VRI instances.
        """
        res = client.get(VRI_URL)

        vris_from_db = VRI.objects.all().filter(date=vris[3].date)
        serialized = VRISerializer(vris_from_db, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 2
        assert res.data[1]['actual_value'] == vris[3].actual_value
        assert res.data == serialized.data
        # Check that the region is not serialized with geometry
        assert res.data[1]['region'].get('actual_value') is None

    def test_retrieve_vri_list_number_of_queries(self, vris, client, connection):
        """
        Retrieve the list of VRI instances and check the number of queries executed.
        """

        res = client.get(VRI_URL)

        assert res.status_code == status.HTTP_200_OK
        # Check that only 2 queries are executed (1 for getting the latest date
        # and 1 for getting the VRI instances with the region joined)
        _ = res.data[1]['actual_value']
        _ = res.data[1]['region']['name']
        assert len(self._get_queries(connection)) == 2

    # TODO: Check format GEOJSON or JSON

    def test_retrieve_vri_list_with_geometry(self, vris, client):
        """
        Retrieve the list of VRI instances with geometry.
        """
        res = client.get(VRI_URL, {'response_format': 'GEOJSON'})

        vris_from_db = VRI.objects.with_geometry().all().filter(date=vris[3].date)
        serialized = VRIWithGeometrySerializer(vris_from_db, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 2
        assert res.data[1]['actual_value'] == vris[3].actual_value
        assert res.data[1]['region']['geometry'] is not None
        assert res.data == serialized.data

    def test_retrieve_vri_list_with_geometry_number_of_queries(self, vris, client, connection):
        """
        Retrieve the list of VRI instances with geometry and check the number of queries executed
        """
        res = client.get(VRI_URL, {'response_format': 'GEOJSON'})

        assert res.status_code == status.HTTP_200_OK
        # Check that only 2 queries are executed (1 for getting the latest date
        # and 1 for getting the VRI instances with the region joined)
        _ = res.data[1]['actual_value']
        _ = res.data[1]['region']['geometry']
        assert len(self._get_queries(connection)) == 2
