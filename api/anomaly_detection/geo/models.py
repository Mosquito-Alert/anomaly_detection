from django.contrib.gis.db import models


class Municipality(models.Model):
    """
    Model to store the municipality data.
    """
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, blank=True, null=True)
    geometry = models.MultiPolygonField()

    province = models.ForeignKey('Province', on_delete=models.CASCADE, related_name='municipalities')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['code']
        indexes = [
            models.Index(fields=['name'])
        ]
        verbose_name = 'Municipality'
        verbose_name_plural = 'Municipalities'


class Province(models.Model):
    """
    Model to store the province data.
    """
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, blank=True, null=True)
    geometry = models.MultiPolygonField()

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
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, blank=True, null=True)
    geometry = models.MultiPolygonField()

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
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, blank=True, null=True)
    continent = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
