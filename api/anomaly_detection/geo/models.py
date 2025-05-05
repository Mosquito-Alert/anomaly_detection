from django.contrib.gis.db import models

from .managers import RegionManager


class AbstractRegion(models.Model):
    """
    Abstract model to store the region data.
    """
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, blank=True, null=True)
    geometry = models.MultiPolygonField()

    # Manager
    objects = RegionManager()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['code']
        indexes = [
            models.Index(fields=['name'])
        ]


class Country(models.Model):
    """
    Model to store the country data.
    """
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, blank=True, null=True)
    continent = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


class AutonomousCommunity(AbstractRegion):
    """
    Model to store the autonomous community data.
    """
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='autonomous_communities')

    class Meta(AbstractRegion.Meta):
        verbose_name = 'Autonomous Community'
        verbose_name_plural = 'Autonomous Communities'


class Province(AbstractRegion):
    """
    Model to store the province data.
    """
    autonomous_community = models.ForeignKey(AutonomousCommunity, on_delete=models.CASCADE, related_name='provinces')

    class Meta(AbstractRegion.Meta):
        verbose_name = 'Province'
        verbose_name_plural = 'Provinces'


class Municipality(AbstractRegion):
    """
    Model to store the municipality data.
    """
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='municipalities')

    class Meta(AbstractRegion.Meta):
        verbose_name = 'Municipality'
        verbose_name_plural = 'Municipalities'
