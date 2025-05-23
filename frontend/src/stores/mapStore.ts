import { FeatureLike } from 'ol/Feature';
import { defineStore, acceptHMRUpdate } from 'pinia';
import { metricsApi } from '../services/apiService';
import { MetricDetail } from 'anomaly-detection';

export const useMapStore = defineStore('mapStore', {
  state: () => ({
    selectedRegionMetric: {} as MetricDetail,
    fetchingRegionMetric: true,
  }),

  getters: {
    isRegionSelected: (state) => Object.keys(state.selectedRegionMetric).length > 0,
    getFormattedRegionMetric: (state): MetricDetail => {
      if (Object.keys(state.selectedRegionMetric).length === 0) {
        return {} as MetricDetail;
      }
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
    async fetchAndSetSelectedMetric(metricUuid: string) {
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
      this.selectedRegionMetric = {} as MetricDetail;
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMapStore, import.meta.hot));
}
