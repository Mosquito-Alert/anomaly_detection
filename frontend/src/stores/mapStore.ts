import { defineStore, acceptHMRUpdate } from 'pinia';
import { metricsApi } from '../services/apiService';
import { MetricDetail, PaginatedMetricList } from 'anomaly-detection';
import { historyPageSize } from '../constants/config';

export const useMapStore = defineStore('mapStore', {
  state: () => ({
    selectedRegionMetricId: '',
    selectedRegionMetric: null as MetricDetail | null,
    selectedRegionHistory: null as PaginatedMetricList | null,
    fetchingRegionMetric: true,
    fetchingRegionHistory: true,
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
    async fetchAndSetSelectedMetricHistory({
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
        this.fetchingRegionHistory = true;
        const response = await metricsApi.list({
          regionCode: this.selectedRegionMetric?.region?.code,
          dateFrom: dateStringFrom,
          dateTo: this.selectedRegionMetric.date,
          page: page,
          pageSize: pageSize,
        });
        if (response.status === 200 && response.data) {
          this.selectedRegionHistory = response.data;
          this.fetchingRegionHistory = false;
        }
      } catch (error) {
        console.error('Error fetching selected region:', error);
      }
    },
    async fetchAndSetSelectedMetric(metricUuid: string): Promise<void> {
      try {
        this.fetchingRegionMetric = true;
        const response = await metricsApi.retrieve({ id: metricUuid });
        if (response.status === 200 && response.data) {
          this.selectedRegionMetric = response.data;
          this.fetchingRegionMetric = false;
        }
      } catch (error) {
        console.error('Error fetching selected region:', error);
      }
    },
    clearSelectedFeatures() {
      this.selectedRegionMetricId = '';
      this.selectedRegionMetric = null;
      this.selectedRegionHistory = null;
      this.fetchingRegionMetric = true;
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMapStore, import.meta.hot));
}
