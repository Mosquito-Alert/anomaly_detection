import { FeatureLike } from 'ol/Feature';
import { defineStore, acceptHMRUpdate } from 'pinia';
import { api } from '../boot/axios';

export const useMapStore = defineStore('mapStore', {
  state: () => ({
    selectedFeatures: [] as FeatureLike[],
    selectedMetric: null,
  }),

  getters: {
    isRegionSelected: (state) => state.selectedFeatures.length > 0,
    getSelectedRegion: (state) => state.selectedFeatures[0] as FeatureLike,
    getSelectedRegionId: (state) => {
      return state.selectedFeatures[0] ? state.selectedFeatures[0].getId() : null;
    },
    getSelectedRegionName: (state) => {
      return state.selectedFeatures[0]
        ? state.selectedFeatures[0].getProperties().region__name
        : null;
    },
    getSelectedRegionAnomalyDegree: (state) => {
      return state.selectedFeatures[0]
        ? state.selectedFeatures[0].getProperties().anomaly_degree
        : null;
    },
  },

  actions: {
    setSelectedFeatures(features: FeatureLike[]) {
      this.selectedFeatures = features;
    },
    clearSelectedFeatures() {
      this.selectedFeatures = [];
    },
    async fetchSelectedMetric(metricUuid: string) {
      try {
        const response = await api.get(`metrics/${metricUuid}/`);
        if (response.status === 200 && response.data) {
        }
      } catch (error) {
        console.error('Error fetching selected region:', error);
      }
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMapStore, import.meta.hot));
}
