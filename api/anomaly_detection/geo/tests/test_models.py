from django.contrib.gis.geos import MultiPolygon, Polygon
from django.db import IntegrityError
import pytest

from anomaly_detection.geo.models import AutonomousCommunity, Country, Geometry, Municipality, Province


@pytest.fixture
def multipolygon():
    """Fixture to create a MultiPolygon instance."""
    # Create a MultiPolygon instance with one polygon
    polygon = Polygon(((0, 0), (1, 1), (1, 0), (0, 0)))
    multipolygon = MultiPolygon(polygon)
    return multipolygon


@pytest.fixture
def geometry(multipolygon):
    """Fixture to create a Geometry instance."""
    return Geometry.objects.create(geometry=multipolygon)


@pytest.fixture
def country():
    """Fixture to create a Country instance."""
    return Country.objects.create(
        gadm_id='ESP',
        name='Spain',
        alt_name='Espana',
        continent='Europe'
    )


@pytest.fixture
def autonomous_community(country):
    """Fixture to create an AutonomousCommunity instance."""
    return AutonomousCommunity.objects.create(
        gadm_id='ESP.1_1',
        name='Test Autonomous Community',
        alt_name='Test Alt Name',
        country=country
    )


@pytest.fixture
def province(autonomous_community):
    """Fixture to create a Province instance."""
    return Province.objects.create(
        gadm_id='ESP.1.1_1',
        name='Test Province',
        alt_name='Test Alt Name',
        autonomous_community=autonomous_community
    )


@pytest.fixture
def municipality(geometry, province):
    """Fixture to create a Municipality instance."""
    return Municipality.objects.create(
        gadm_id='ESP.1.1.1.1_1',
        name='Test Municipality',
        alt_name='Test Alt Name',
        geometry=geometry,
        province=province
    )


@pytest.mark.django_db
class TestGeometryModel:
    """Test case for the Geometry model."""

    def test_geometry_creation(self, multipolygon, geometry):
        """Test the creation of a Geometry instance."""
        assert isinstance(geometry, Geometry)
        assert geometry.geometry == multipolygon


@pytest.mark.django_db
class TestMunicipalityModel:
    """Test case for the Municipality model."""

    def test_municipality_creation(self, geometry, province, municipality):
        """Test the creation of a Municipality instance."""
        assert isinstance(municipality, Municipality)
        assert municipality.gadm_id == 'ESP.1.1.1.1_1'
        assert municipality.name == 'Test Municipality'
        assert municipality.alt_name == 'Test Alt Name'
        assert municipality.geometry == geometry
        assert municipality.province == province

    def test_municipality_str(self, municipality):
        """Test the string representation of a Municipality instance."""
        assert str(municipality) == 'Test Municipality'

    def test_municipality_meta(self, municipality):
        """Test the meta options of the Municipality model."""
        assert Municipality._meta.verbose_name == 'Municipality'
        assert Municipality._meta.verbose_name_plural == 'Municipalities'
        assert Municipality._meta.ordering == ['gadm_id']
        assert 'name' in [field for field in Municipality._meta.indexes[0].fields]

    def test_municipality_geometry_relation(self, geometry, municipality):
        """Test the one-to-one relationship between Municipality and Geometry."""
        assert municipality.geometry == geometry
        assert geometry.region == municipality

    def test_municipality_geometry_cannot_be_null(self, province):
        """Test that the geometry field cannot be null."""
        with pytest.raises(IntegrityError):
            Municipality.objects.create(
                gadm_id='ESP.1.1.1.2_1',
                name='Test Municipality 2',
                alt_name='Test Alt Name 2',
                province=province
            )

    def test_municipality_province_relation(self, province, municipality):
        """Test the foreign key relationship between Municipality and Province."""
        assert municipality.province == province
        assert municipality in province.municipalities.all()

    def test_municipality_province_cannot_be_null(self, geometry):
        """Test that the province field cannot be null."""
        with pytest.raises(IntegrityError):
            Municipality.objects.create(
                gadm_id='ESP.1.1.1.3_1',
                name='Test Municipality 3',
                alt_name='Test Alt Name 3',
                geometry=geometry
            )


@pytest.mark.django_db
class TestProvinceModel:
    """Test case for the Province model."""

    def test_province_creation(self, autonomous_community, province):
        """Test the creation of a Province instance."""
        assert isinstance(province, Province)
        assert province.gadm_id == 'ESP.1.1_1'
        assert province.name == 'Test Province'
        assert province.alt_name == 'Test Alt Name'
        assert province.autonomous_community == autonomous_community

    def test_province_str(self, province):
        """Test the string representation of a Province instance."""
        assert str(province) == 'Test Province'

    def test_province_meta(self):
        """Test the meta options of the Province model."""
        assert Province._meta.verbose_name == 'Province'
        assert Province._meta.verbose_name_plural == 'Provinces'

    def test_province_autonomous_community_relation(self, autonomous_community, province):
        """Test the foreign key relationship between Province and AutonomousCommunity."""
        assert province.autonomous_community == autonomous_community
        assert province in autonomous_community.provinces.all()

    def test_province_autonomous_community_cannot_be_null(self):
        """Test that the autonomous community field cannot be null."""
        with pytest.raises(IntegrityError):
            Province.objects.create(
                gadm_id='ESP.1.1_2',
                name='Test Province 2',
                alt_name='Test Alt Name 2'
            )


@pytest.mark.django_db
class TestAutonomousCommunityModel:
    """Test case for the AutonomousCommunity model."""

    def test_autonomous_community_creation(self, country, autonomous_community):
        """Test the creation of an AutonomousCommunity instance."""
        assert isinstance(autonomous_community, AutonomousCommunity)
        assert autonomous_community.gadm_id == 'ESP.1_1'
        assert autonomous_community.name == 'Test Autonomous Community'
        assert autonomous_community.alt_name == 'Test Alt Name'
        assert autonomous_community.country == country

    def test_autonomous_community_str(self, autonomous_community):
        """Test the string representation of an AutonomousCommunity instance."""
        assert str(autonomous_community) == 'Test Autonomous Community'

    def test_autonomous_community_meta(self):
        """Test the meta options of the AutonomousCommunity model."""
        assert AutonomousCommunity._meta.verbose_name == 'Autonomous Community'
        assert AutonomousCommunity._meta.verbose_name_plural == 'Autonomous Communities'


@pytest.mark.django_db
class TestCountryModel:
    """Test case for the Country model."""

    def test_country_creation(self, country):
        """Test the creation of a Country instance."""
        assert isinstance(country, Country)
        assert country.gadm_id == 'ESP'
        assert country.name == 'Spain'
        assert country.alt_name == 'Espana'
        assert country.continent == 'Europe'

    def test_country_str(self, country):
        """Test the string representation of a Country instance."""
        assert str(country) == 'Spain'

    def test_country_meta(self):
        """Test the meta options of the Country model."""
        assert Country._meta.verbose_name == 'Country'
        assert Country._meta.verbose_name_plural == 'Countries'
