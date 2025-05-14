
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from anomaly_detection.predictions.models import Metric, MetricExecution


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('id', 'region', 'date', 'anomaly_degree')
    search_fields = ('region__name', 'date', 'anomaly_degree')
    list_filter = ('date', 'region')
    ordering = ['-date']
    fieldsets = (
        (_('General'), {
            'fields': ['region', 'date']
        }),
        (_('Values'), {
            'fields': ['anomaly_degree', 'value', 'predicted_value', 'lower_value', 'upper_value', 'trend']
        }),
        (_('Dates'), {
            'fields': ['created_at', 'updated_at']
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'anomaly_degree']


# @admin.register(MetricSeasonality)
# class MetricSeasonalityAdmin(admin.ModelAdmin):
#     list_display = ('id', 'region', 'index', 'yearly_value')
#     search_fields = ['region__name']
#     list_filter = ['region']
#     ordering = ['index']
#     fieldsets = (
#         (_('General'), {
#             'fields': ['region', 'index', 'yearly_value']
#         }),
#         (_('Dates'), {
#             'fields': ['created_at', 'updated_at']
#         }),
#     )
#     readonly_fields = ['created_at', 'updated_at']


@admin.register(MetricExecution)
class MetricExecutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'success_percentage')
    list_filter = ['date']
    ordering = ['-date']
    fieldsets = (
        (_('General'), {
            'fields': ['date', 'success_percentage']
        }),
    )
