import pytest
from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.db import connection, reset_queries

from anomaly_detection.geo.models import (AutonomousCommunity, Country,
                                          Municipality, Province)
from anomaly_detection.vri.models import VRI, VRISeasonality


@pytest.fixture
def multipolygon():
    """Fixture to create a MultiPolygon instance."""
    # Create a MultiPolygon instance with one polygon
    polygon = Polygon(((0, 0), (1, 1), (1, 0), (0, 0)))
    multipolygon = MultiPolygon(polygon)
    return multipolygon


@pytest.fixture
def municipality(multipolygon):
    """Fixture to create a Municipality instance."""
    country = Country.objects.create(
        code='ESP',
        name='Spain',
        alt_name='Espana',
        continent='Europe',
    )
    autonomous_community = AutonomousCommunity.objects.create(
        code='ESP.1_1',
        name='Test Autonomous Community',
        alt_name='Test Alt Name',
        country=country,
        geometry=multipolygon
    )
    province = Province.objects.create(
        code='ESP.1.1_1',
        name='Test Province',
        alt_name='Test Alt Name',
        autonomous_community=autonomous_community,
        geometry=multipolygon
    )
    return Municipality.objects.create(
        code='ESP.1.1.1.1_1',
        name='Test Municipality',
        alt_name='Test Alt Name',
        province=province,
        geometry=multipolygon
    )


# TODO: Use factory_boy
@pytest.fixture
def vris(municipality):
    """Fixture to create a VRI instance."""
    vri1 = VRI.objects.create(
        region=municipality,
        date='2023-01-01',
        actual_value=0.8,
        predicted_value=0.85,
        lower_value=0.5,
        upper_value=1.0,
        trend=0.1,
    )
    vri2 = VRI.objects.create(
        region=municipality,
        date='2023-01-02',
        actual_value=0.9,
        predicted_value=0.75,
        lower_value=0.6,
        upper_value=0.8,
        trend=0.2,
    )
    vri3 = VRI.objects.create(
        region=municipality,
        date='2023-01-03',
        actual_value=0.4,
        predicted_value=0.75,
        lower_value=0.5,
        upper_value=0.9,
        trend=0.3,
    )
    return vri1, vri2, vri3


@pytest.fixture
def seasonalities(municipality):
    """Fixture to create a VRISeasonality instance."""
    seasonality1 = VRISeasonality.objects.create(
        region=municipality,
        index=0,
        yearly_value=0.5
    )
    seasonality2 = VRISeasonality.objects.create(
        region=municipality,
        index=1,
        yearly_value=0.6
    )
    return seasonality1, seasonality2


@pytest.mark.django_db
class TestVRIModel:
    """
    Test the VRI model.
    """

    def test_vri_creation(self, vris, municipality):
        """
        Test the creation of a VRI instance.
        """
        vri1, vri2, vri3 = vris
        assert isinstance(vri1, VRI)
        assert vri1.region.code == 'ESP.1.1.1.1_1'
        assert vri2.date == '2023-01-02'
        assert vri1.region == municipality

    def test_vri_str(self, vris):
        """
        Test the string representation of a VRI instance.
        """
        vri1, _, _ = vris
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
        vri1, vri2, vri3 = vris
        assert vri2.anomaly_degree is not None
        assert isinstance(vri2.anomaly_degree, float)
        assert vri1.anomaly_degree == 0.0
        assert vri2.anomaly_degree == (vri2.actual_value - vri2.upper_value) / vri2.actual_value
        assert vri3.anomaly_degree == (vri3.actual_value - vri3.lower_value) / vri3.actual_value

    def test_vri_region(self, vris, multipolygon):
        """
        Test the region field of the VRI model.
        """
        vri1, _, _ = vris
        assert vri1.region is not None
        assert isinstance(vri1.region, Municipality)
        assert vri1.region.code == 'ESP.1.1.1.1_1'
        assert vri1.region.name == 'Test Municipality'
        assert vri1.region.geometry == multipolygon

    def test_vri_region_geometry_deferred_by_default(self, vris):
        """
        Test that the geometry field is deferred by default.
        """
        settings.DEBUG = True  # Enable DEBUG mode for testing
        # Reset queries to count the number of queries executed
        reset_queries()

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

    def test_vri_region_with_geometry(self, vris):
        """
        Test that the region field with geometry is not deferred.
        """
        settings.DEBUG = True  # Enable DEBUG mode for testing
        # Reset queries to count the number of queries executed
        reset_queries()

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
        seasonality1, seasonality2 = seasonalities
        assert isinstance(seasonality1, VRISeasonality)
        assert seasonality1.region.code == 'ESP.1.1.1.1_1'
        assert seasonality2.yearly_value == 0.6
        assert seasonality1.region == municipality

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

    def test_vri_seasonality_region_geometry_deferred_by_default(self, seasonalities):
        """
        Test that the geometry field is deferred by default.
        """
        settings.DEBUG = True

        # Reset queries to count the number of queries executed
        reset_queries()

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

    def test_vri_seasonality_region_with_geometry(self, seasonalities):
        """
        Test that the region field with geometry is not deferred.
        """
        settings.DEBUG = True

        # Reset queries to count the number of queries executed
        reset_queries()

        # Get the first VRISeasonality instance
        seasonality1 = VRISeasonality.objects.with_geometry().first()

        # Accessing region with geometry should NOT trigger additional query
        _ = seasonality1.region.geometry
        queries_after_geometry = len(connection.queries)

        assert queries_after_geometry == 1
