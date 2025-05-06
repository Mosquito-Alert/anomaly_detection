

from django.urls import reverse
import pytest
from rest_framework import status

from anomaly_detection.vri.models import VRI
from anomaly_detection.vri.serializers import VRISerializer


VRI_URL = reverse('vri:vri-list')


@pytest.mark.django_db
class TestVRIListView:
    """
    Tests the VRI View for the List action.
    """

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

    # TODO: Check results with and without geometry: query param (geometry=true), GEOJSON etc
