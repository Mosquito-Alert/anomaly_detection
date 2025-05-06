import pytest
from django.contrib.gis.geos import MultiPolygon, Polygon

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
    municipality1 = Municipality.objects.create(
        code='ESP.1.1.1.1_1',
        name='Test Municipality',
        alt_name='Test Alt Name',
        province=province,
        geometry=multipolygon
    )
    municipality2 = Municipality.objects.create(
        code='ESP.1.1.1.2_1',
        name='Test Municipality 2',
        alt_name='Test Alt Name 2',
        province=province,
        geometry=multipolygon
    )
    return municipality1, municipality2


# TODO: Use factory_boy
@pytest.fixture
def vris(municipality):
    """Fixture to create a VRI instance."""
    municipality1, municipality2 = municipality
    vri1 = VRI.objects.create(
        region=municipality1,
        date='2023-01-01',
        actual_value=0.8,
        predicted_value=0.85,
        lower_value=0.5,
        upper_value=1.0,
        trend=0.1,
    )
    vri2 = VRI.objects.create(
        region=municipality1,
        date='2023-01-02',
        actual_value=0.9,
        predicted_value=0.75,
        lower_value=0.6,
        upper_value=0.8,
        trend=0.2,
    )
    vri3 = VRI.objects.create(
        region=municipality1,
        date='2023-01-03',
        actual_value=0.4,
        predicted_value=0.75,
        lower_value=0.5,
        upper_value=0.9,
        trend=0.3,
    )
    vri4 = VRI.objects.create(
        region=municipality2,
        date='2023-01-03',
        actual_value=0.7,
        predicted_value=0.85,
        lower_value=0.4,
        upper_value=0.9,
        trend=0.1,
    )
    return vri1, vri2, vri3, vri4


@pytest.fixture
def seasonalities(municipality):
    """Fixture to create a VRISeasonality instance."""
    municipality1, _ = municipality
    seasonality1 = VRISeasonality.objects.create(
        region=municipality1,
        index=0,
        yearly_value=0.5
    )
    seasonality2 = VRISeasonality.objects.create(
        region=municipality1,
        index=1,
        yearly_value=0.6
    )
    return seasonality1, seasonality2
