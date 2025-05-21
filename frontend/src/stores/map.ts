import { FeatureLike } from 'ol/Feature';
import { defineStore, acceptHMRUpdate } from 'pinia';

export const useMapStore = defineStore('mapStore', {
  state: () => ({
    selectedFeatures: [] as FeatureLike[],
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
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMapStore, import.meta.hot));
}
