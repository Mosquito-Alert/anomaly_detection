import { FeatureLike } from 'ol/Feature';
import { defineStore, acceptHMRUpdate } from 'pinia';
import { metricsApi } from '../services/apiService';
import { MetricDetail } from 'anomaly-detection';

export const useMapStore = defineStore('mapStore', {
  state: () => ({
    selectedRegionMetric: {} as MetricDetail,
  }),

  getters: {
    isRegionSelected: (state) => Object.keys(state.selectedRegionMetric).length > 0,
  },

  actions: {
    async fetchAndSetSelectedMetric(metricUuid: string) {
      try {
        const response = await metricsApi.retrieve({ id: metricUuid });
        if (response.status === 200 && response.data) {
          this.selectedRegionMetric = response.data;
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
