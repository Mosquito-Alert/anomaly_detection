from django.test import TestCase

from api.anomaly_detection.geo.models import AutonomousCommunity, Country, Geometry, Municipality, Province


class GeometryModelTests(TestCase):
    """Test case for the Geometry model."""

    def setUp(self):
        """Set up the test case."""
        # Create a Geometry instance
        self.geometry = Geometry.objects.create(geometry='MULTIPOLYGON (((0 0, 1 1, 1 0, 0 0)))')

    def test_geometry_creation(self):
        """Test the creation of a Geometry instance."""
        self.assertIsInstance(self.geometry, Geometry)
        self.assertEqual(self.geometry.geometry, 'MULTIPOLYGON (((0 0, 1 1, 1 0, 0 0)))')


class MunicipalityModelTests(TestCase):
    """Test case for the Municipality model."""

    def setUp(self):
        """Set up the test case."""
        self.geometry = Geometry.objects.create(geometry='MULTIPOLYGON (((0 0, 1 1, 1 0, 0 0)))')
        self.province = Province.objects.create(
            gadm_id='ESP.1.1.1_1',
            name='Test Province',
            alt_name='Test Alt Name',
            autonomous_community=self.autonomous_community
        )

        # Create a Municipality instance
        self.municipality = Municipality.objects.create(
            gadm_id='ESP.1.1.1.1_1',
            name='Test Municipality',
            alt_name='Test Alt Name',
            geometry=self.geometry,
            province=self.province
        )

    def test_municipality_creation(self):
        """Test the creation of a Municipality instance."""
        self.assertIsInstance(self.municipality, Municipality)
        self.assertEqual(self.municipality.gadm_id, 'ESP.1.1.1.1_1')
        self.assertEqual(self.municipality.name, 'Test Municipality')
        self.assertEqual(self.municipality.alt_name, 'Test Alt Name')
        self.assertEqual(self.municipality.geometry, self.geometry)
        self.assertEqual(self.municipality.province, self.province)

    def test_municipality_str(self):
        """Test the string representation of a Municipality instance."""
        self.assertEqual(str(self.municipality), 'Test Municipality')

    def test_municipality_meta(self):
        """Test the meta options of the Municipality model."""
        self.assertEqual(Municipality._meta.verbose_name, 'Municipality')
        self.assertEqual(Municipality._meta.verbose_name_plural, 'Municipalities')
        self.assertEqual(Municipality._meta.ordering, ['gadm_id'])
        self.assertIn('name', [field.name for field in Municipality._meta.indexes[0].fields])

    def test_municipality_geometry_relation(self):
        """Test the one-to-one relationship between Municipality and Geometry."""
        self.assertEqual(self.municipality.geometry, self.geometry)
        self.assertEqual(self.geometry.region, self.municipality)

    def test_municipality_geometry_cannot_be_null(self):
        """Test that the geometry field cannot be null."""
        with self.assertRaises(ValueError):
            Municipality.objects.create(
                gadm_id='ESP.1.1.1.2_1',
                name='Test Municipality 2',
                alt_name='Test Alt Name 2'
            )

    def test_municipality_province_relation(self):
        """Test the foreign key relationship between Municipality and Province."""
        self.assertEqual(self.municipality.province, self.province)
        self.assertIn(self.municipality, self.province.municipalities.all())

    def test_municipality_province_cannot_be_null(self):
        """Test that the province field cannot be null."""
        with self.assertRaises(ValueError):
            Municipality.objects.create(
                gadm_id='ESP.1.1.1.3_1',
                name='Test Municipality 3',
                alt_name='Test Alt Name 3',
                geometry=self.geometry
            )


class ProvinceModelTests(TestCase):
    """Test case for the Province model."""

    def setUp(self):
        """Set up the test case."""
        self.autonomous_community = AutonomousCommunity.objects.create(
            gadm_id='ESP.1.1_1',
            name='Test Autonomous Community',
            alt_name='Test Alt Name'
        )

        # Create a Province instance
        self.province = Province.objects.create(
            gadm_id='ESP.1.1_1',
            name='Test Province',
            alt_name='Test Alt Name',
            autonomous_community=self.autonomous_community
        )

    def test_province_creation(self):
        """Test the creation of a Province instance."""
        self.assertIsInstance(self.province, Province)
        self.assertEqual(self.province.gadm_id, 'ESP.1.1_1')
        self.assertEqual(self.province.name, 'Test Province')
        self.assertEqual(self.province.alt_name, 'Test Alt Name')
        self.assertEqual(self.province.autonomous_community, self.autonomous_community)

    def test_province_str(self):
        """Test the string representation of a Province instance."""
        self.assertEqual(str(self.province), 'Test Province')

    def test_province_autonomous_community_relation(self):
        """Test the foreign key relationship between Province and AutonomousCommunity."""
        self.assertEqual(self.province.autonomous_community, self.autonomous_community)
        self.assertIn(self.province, self.autonomous_community.provinces.all())

    def test_province_autonomous_community_cannot_be_null(self):
        """Test that the autonomous community field cannot be null."""
        with self.assertRaises(ValueError):
            Province.objects.create(
                gadm_id='ESP.1.1_2',
                name='Test Province 2',
                alt_name='Test Alt Name 2'
            )


class AutonomousCommunityModelTests(TestCase):
    """Test case for the AutonomousCommunity model."""

    def setUp(self):
        """Set up the test case."""
        # Create an AutonomousCommunity instance
        self.autonomous_community = AutonomousCommunity.objects.create(
            gadm_id='ESP.1_1',
            name='Test Autonomous Community',
            alt_name='Test Alt Name'
        )

    def test_autonomous_community_creation(self):
        """Test the creation of an AutonomousCommunity instance."""
        self.assertIsInstance(self.autonomous_community, AutonomousCommunity)
        self.assertEqual(self.autonomous_community.gadm_id, 'ESP.1_1')
        self.assertEqual(self.autonomous_community.name, 'Test Autonomous Community')
        self.assertEqual(self.autonomous_community.alt_name, 'Test Alt Name')

    def test_autonomous_community_str(self):
        """Test the string representation of an AutonomousCommunity instance."""
        self.assertEqual(str(self.autonomous_community), 'Test Autonomous Community')

    def test_autonomous_community_country_relation(self):
        """Test the foreign key relationship between AutonomousCommunity and Country."""
        self.assertEqual(self.autonomous_community.country, self.country)
        self.assertIn(self.autonomous_community, self.country.autonomous_communities.all())

    def test_autonomous_community_country_cannot_be_null(self):
        """Test that the country field cannot be null."""
        with self.assertRaises(ValueError):
            AutonomousCommunity.objects.create(
                gadm_id='ESP.1_2',
                name='Test Autonomous Community 2',
                alt_name='Test Alt Name 2'
            )


class CountryModelTests(TestCase):
    """Test case for the Country model."""

    def setUp(self):
        """Set up the test case."""
        # Create a Country instance
        self.country = Country.objects.create(
            gadm_id='ESP',
            name='Spain',
            alt_name='Espana',
            continent='Europe'
        )

    def test_country_creation(self):
        """Test the creation of a Country instance."""
        self.assertIsInstance(self.country, Country)
        self.assertEqual(self.country.gadm_id, 'ESP')
        self.assertEqual(self.country.name, 'Spain')
        self.assertEqual(self.country.alt_name, 'Espana')
        self.assertEqual(self.country.continent, 'Europe')

    def test_country_str(self):
        """Test the string representation of a Country instance."""
        self.assertEqual(str(self.country), 'Spain')
