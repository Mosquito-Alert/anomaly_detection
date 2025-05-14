from django.db.models import Manager, Prefetch

from anomaly_detection.geo.models import Municipality


class RegionSelectedManager(Manager):
    """
    Custom manager for the Region model.
    """

    def get_queryset(self):
        """
        Override the default queryset to return the results with the region selected, and
        the geometry field of the region deferred.
        These are useful for performance reasons (one query and not retrieving the geometry field
        by default).
        """
        return super().get_queryset().select_related('region').defer('region__geometry')

    def with_geometry(self):
        """
        Return the queryset with the geometry field included.
        This is useful for when you need to access the geometry data.
        """
        return super().get_queryset().select_related('region').prefetch_related(
            Prefetch('region', queryset=Municipality.objects.with_geometry())  # .filter(pk=OuterRef('region'))
        )

# class PredictorManager(Manager):
    # TODO: get_not_expire(region_id, date)
