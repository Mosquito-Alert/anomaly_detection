from django.contrib.gis.db import models


class Geometry(models.Model):
    """
    Model to store the geometry of a region.
    """
    geometry = models.MultiPolygonField()

    class Meta:
        verbose_name = 'Geometry'
        verbose_name_plural = 'Geometries'


class Municipality(models.Model):
    """
    Model to store the municipality data.
    """
    gadm_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, blank=True, null=True)

    geometry = models.OneToOneField(Geometry, on_delete=models.CASCADE, related_name='region')
    province = models.ForeignKey('Province', on_delete=models.CASCADE, related_name='municipalities')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['gadm_id']
        indexes = [
            models.Index(fields=['name'])
        ]
        verbose_name = 'Municipality'
        verbose_name_plural = 'Municipalities'


class Province(models.Model):
    """
    Model to store the province data.
    """
    gadm_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, blank=True, null=True)
    autonomous_community = models.ForeignKey('AutonomousCommunity', on_delete=models.CASCADE, related_name='provinces')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Province'
        verbose_name_plural = 'Provinces'


class AutonomousCommunity(models.Model):
    """
    Model to store the autonomous community data.
    """
    gadm_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='autonomous_communities')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Autonomous Community'
        verbose_name_plural = 'Autonomous Communities'


class Country(models.Model):
    """
    Model to store the country data.
    """
    gadm_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, blank=True, null=True)
    continent = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
