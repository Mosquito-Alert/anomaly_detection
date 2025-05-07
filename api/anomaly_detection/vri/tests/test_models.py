import pytest

from anomaly_detection.geo.models import Municipality
from anomaly_detection.vri.models import VRI, VRISeasonality


@pytest.mark.django_db
class TestVRIModel:
    """
    Test the VRI model.
    """

    def test_vri_creation(self, vris, municipality):
        """
        Test the creation of a VRI instance.
        """
        municipality1, _ = municipality
        vri1, vri2, _, _ = vris
        assert isinstance(vri1, VRI)
        assert vri1.region.code == 'ESP.1.1.1.1_1'
        assert vri2.date == '2023-01-02'
        assert vri1.region == municipality1

    def test_vri_str(self, vris):
        """
        Test the string representation of a VRI instance.
        """
        vri1, _, _, _ = vris
        assert str(vri1) == f"VRI for {vri1.region.name} on {vri1.date}: {vri1.actual_value}"

    def test_vri_meta(self):
        """
        Test the Meta class of the VRI model.
        """
        assert VRI._meta.verbose_name == 'Vector Risk Index'
        assert VRI._meta.verbose_name_plural == 'Vector Risk Indexes'
        assert VRI._meta.ordering == ['region', '-date']
        assert VRI._meta.indexes[0].fields == ['date']
        assert VRI._meta.indexes[1].fields == ['region', 'date']
        assert VRI._meta.unique_together is not None

    def test_vri_anomaly_degree(self, vris):
        """
        Test the anomaly degree calculation.
        """
        vri1, vri2, vri3, _ = vris
        assert vri2.anomaly_degree is not None
        assert isinstance(vri2.anomaly_degree, float)
        assert vri1.anomaly_degree == 0.0
        assert vri2.anomaly_degree == (vri2.actual_value - vri2.upper_value) / vri2.actual_value
        assert vri3.anomaly_degree == (vri3.actual_value - vri3.lower_value) / vri3.actual_value

    def test_vri_region(self, vris, multipolygon):
        """
        Test the region field of the VRI model.
        """
        vri1, _, _, _ = vris
        assert vri1.region is not None
        assert isinstance(vri1.region, Municipality)
        assert vri1.region.code == 'ESP.1.1.1.1_1'
        assert vri1.region.name == 'Test Municipality'
        assert vri1.region.geometry == multipolygon

    def test_vri_region_geometry_deferred_by_default(self, vris, connection):
        """
        Test that the geometry field is deferred by default.
        """
        # Get the first VRI instance
        vri1 = VRI.objects.first()

        # Accessing region should NOT trigger additional query
        _ = vri1.region
        queries_after_region = len(connection.queries)

        # Accessing geometry SHOULD trigger additional query (deferred)
        _ = vri1.region.geometry
        queries_after_geometry = len(connection.queries)

        assert queries_after_region == 1
        assert queries_after_geometry == 2

    def test_vri_region_with_geometry(self, vris, connection):
        """
        Test that the region field with geometry is not deferred.
        """

        # Get the first VRI instance
        vri1 = VRI.objects.with_geometry().first()

        # Accessing region with geometry should NOT trigger additional query
        _ = vri1.region.geometry
        queries_after_geometry = len(connection.queries)

        assert queries_after_geometry == 1


@pytest.mark.django_db
class TestVRISeasonalityModel:
    """
    Test the VRISeasonality model.
    """

    def test_vri_seasonality_creation(self, seasonalities, municipality):
        """
        Test the creation of a VRISeasonality instance.
        """
        municipality1, _ = municipality
        seasonality1, seasonality2 = seasonalities
        assert isinstance(seasonality1, VRISeasonality)
        assert seasonality1.region.code == 'ESP.1.1.1.1_1'
        assert seasonality2.yearly_value == 0.6
        assert seasonality1.region == municipality1

    def test_vri_seasonality_str(self, seasonalities):
        """
        Test the string representation of a VRISeasonality instance.
        """
        seasonality1, _ = seasonalities
        assert str(
            seasonality1) == (
                f"VRI Seasonality for {seasonality1.region.name} on day {seasonality1.index + 1}: "
                f"{seasonality1.yearly_value}"
        )

    def test_vri_seasonality_meta(self):
        """
        Test the Meta class of the VRISeasonality model.
        """
        assert VRISeasonality._meta.verbose_name == 'VRI Seasonality'
        assert VRISeasonality._meta.verbose_name_plural == 'VRI Seasonalities'
        assert VRISeasonality._meta.ordering == ['region', 'index']
        assert VRISeasonality._meta.indexes[0].fields == ['index']
        assert VRISeasonality._meta.unique_together is not None

    def test_vri_seasonality_region(self, seasonalities, multipolygon):
        """
        Test the region field of the VRISeasonality model.
        """
        seasonality1, _ = seasonalities
        assert seasonality1.region is not None
        assert isinstance(seasonality1.region, Municipality)
        assert seasonality1.region.code == 'ESP.1.1.1.1_1'
        assert seasonality1.region.name == 'Test Municipality'
        assert seasonality1.region.geometry == multipolygon

    def test_vri_seasonality_region_geometry_deferred_by_default(self, seasonalities, connection):
        """
        Test that the geometry field is deferred by default.
        """
        # Get the first VRISeasonality instance
        seasonality1 = VRISeasonality.objects.first()

        # Accessing region should NOT trigger additional query
        _ = seasonality1.region
        queries_after_region = len(connection.queries)

        # Accessing geometry SHOULD trigger additional query (deferred)
        _ = seasonality1.region.geometry
        queries_after_geometry = len(connection.queries)

        assert queries_after_region == 1
        assert queries_after_geometry == 2

    def test_vri_seasonality_region_with_geometry(self, seasonalities, connection):
        """
        Test that the region field with geometry is not deferred.
        """
        # Get the first VRISeasonality instance
        seasonality1 = VRISeasonality.objects.with_geometry().first()

        # Accessing region with geometry should NOT trigger additional query
        _ = seasonality1.region.geometry
        queries_after_geometry = len(connection.queries)

        assert queries_after_geometry == 1
