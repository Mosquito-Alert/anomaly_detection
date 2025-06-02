import { defineStore, acceptHMRUpdate } from 'pinia';
import { metricsApi, regionsApi } from '../services/apiService';
import {
  MetricDetail,
  MetricSeasonality,
  MetricTrend,
  Municipality,
  PaginatedMetricList,
} from 'anomaly-detection';
import { historyPageSize } from '../constants/config';
import { FeatureLike } from 'ol/Feature';
import { GeoJSON } from 'ol/format';

export const useMapStore = defineStore('mapStore', {
  state: () => ({
    selectedRegionMetricId: '',
    selectedFeatures: [] as FeatureLike[],
    selectedRegion: null as Municipality | null,
    selectedRegionMetric: null as MetricDetail | null,
    fetchingRegionMetric: true,
    selectedRegionMetricsHistory: null as PaginatedMetricList | null,
    fetchingRegionMetricsHistory: true,
    selectedRegionMetricsAll: null as PaginatedMetricList | null,
    fetchingRegionMetricsAll: true,
    selectedRegionMetricTrend: null as MetricTrend | null,
    fetchingRegionMetricTrend: true,
    selectedRegionMetricSeasonality: null as MetricSeasonality | null,
    fetchingRegionMetricSeasonality: true,
  }),

  getters: {
    isRegionSelected: (state): boolean => state.selectedRegionMetricId !== '',
    getFormattedRegionMetric: (state): MetricDetail | null => {
      if (!state.selectedRegionMetric) return null;
      const { value, predicted_value, lower_value, upper_value, anomaly_degree } =
        state.selectedRegionMetric;
      const roundPercent = (value: number): number => Math.round(value * 1000) / 10;
      return {
        ...state.selectedRegionMetric,
        value: value ? roundPercent(value) : 0,
        predicted_value: predicted_value ? roundPercent(predicted_value) : 0,
        lower_value: lower_value ? roundPercent(lower_value) : 0,
        upper_value: upper_value ? roundPercent(upper_value) : 0,
        anomaly_degree: anomaly_degree ? roundPercent(anomaly_degree) : 0,
      };
    },
  },

  actions: {
    async fetchSelectedRegion(id: number): Promise<void> {
      try {
        const response = await regionsApi.retrieve({ id: id });
        if (response.status === 200 && response.data) {
          const format = new GeoJSON();
          const feature = format.readFeature(response.data.geometry, {
            featureProjection: 'EPSG:3857',
          });
          this.selectedFeatures = [feature as FeatureLike];
        } else {
          throw new Error('Failed to fetch selected region');
        }
      } catch (error) {
        console.error('Error fetching selected region:', error);
      }
    },
    async fetchSelectedMetric(metricUuid: string): Promise<void> {
      try {
        this.fetchingRegionMetric = true;
        const response = await metricsApi.retrieve({ id: metricUuid });
        if (response.status === 200 && response.data) {
          this.selectedRegionMetric = response.data;
          this.fetchingRegionMetric = false;
        } else {
          throw new Error('Failed to fetch selected region metric');
        }
      } catch (error) {
        console.error('Error fetching selected region:', error);
      }
    },
    async fetchSelectedMetricHistory({
      daysSince = 30,
      page = 1,
      pageSize = historyPageSize,
    }: {
      daysSince?: number;
      page?: number;
      pageSize?: number;
    }): Promise<void> {
      if (!this.selectedRegionMetric || !this.selectedRegionMetric?.region) return;
      // Get the date from 30 days before the selected date
      const dateFrom = new Date(this.selectedRegionMetric?.date || new Date());
      dateFrom.setDate(dateFrom.getDate() - daysSince);
      const dateStringFrom = dateFrom.toISOString().split('T')[0] || '';
      try {
        this.fetchingRegionMetricsHistory = true;
        const response = await metricsApi.list({
          regionCode: this.selectedRegionMetric?.region?.code,
          dateFrom: dateStringFrom,
          dateTo: this.selectedRegionMetric.date,
          page: page,
          pageSize: pageSize,
        });
        if (response.status === 200 && response.data) {
          this.selectedRegionMetricsHistory = response.data;
          this.fetchingRegionMetricsHistory = false;
        } else {
          throw new Error('Failed to fetch history for the selected region');
        }
      } catch (error) {
        console.error('Error fetching selected region:', error);
      }
    },
    async fetchSelectedMetricAll(): Promise<void> {
      // TODO: Improve this to fetch all metrics (change API to support this)
      const daysSince = 10 * 365; // Last 10 years
      const pageSize = 10000000; // Large page size to fetch all metrics
      if (!this.selectedRegionMetric || !this.selectedRegionMetric?.region) return;

      const dateFrom = new Date(this.selectedRegionMetric?.date || new Date());
      dateFrom.setDate(dateFrom.getDate() - daysSince);
      const dateStringFrom = dateFrom.toISOString().split('T')[0] || '';

      try {
        this.fetchingRegionMetricsAll = true;
        const response = await metricsApi.list({
          regionCode: this.selectedRegionMetric?.region?.code,
          dateFrom: dateStringFrom,
          dateTo: this.selectedRegionMetric.date,
          page: 1,
          pageSize: pageSize,
          ordering: 'date',
        });
        if (response.status === 200 && response.data) {
          this.selectedRegionMetricsAll = response.data;
          this.fetchingRegionMetricsAll = false;
        } else {
          throw new Error('Failed to fetch all metrics for the selected region');
        }
      } catch (error) {
        console.error('Error fetching selected region:', error);
      }
    },
    async fetchSelectedMetricTrend(): Promise<void> {
      if (!this.selectedRegionMetric || !this.selectedRegionMetric?.region) return;

      try {
        this.fetchingRegionMetricTrend = true;
        const response = await metricsApi.trendRetrieve({
          id: this.selectedRegionMetric?.id,
        });
        if (response.status === 200 && response.data) {
          this.selectedRegionMetricTrend = response.data;
          this.fetchingRegionMetricTrend = false;
        } else {
          throw new Error('Failed to fetch trend for the selected region');
        }
      } catch (error) {
        console.error('Error fetching selected region trend:', error);
      }
    },
    async fetchSelectedMetricSeasonality(): Promise<void> {
      if (!this.selectedRegionMetric || !this.selectedRegionMetric?.region) return;

      try {
        this.fetchingRegionMetricSeasonality = true;
        const response = await metricsApi.seasonalityRetrieve({
          id: this.selectedRegionMetric?.id,
        });
        if (response.status === 200 && response.data) {
          this.selectedRegionMetricSeasonality = response.data;
          this.fetchingRegionMetricSeasonality = false;
        } else {
          throw new Error('Failed to fetch seasonality for the selected region');
        }
      } catch (error) {
        console.error('Error fetching selected region seasonality:', error);
      }
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMapStore, import.meta.hot));
}
