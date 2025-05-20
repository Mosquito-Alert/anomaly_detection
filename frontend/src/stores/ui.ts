import { defineStore, acceptHMRUpdate } from 'pinia';

export const useUIStore = defineStore('myStore', {
  state: () => ({
    showDrawer: false,
  }),

  getters: {
    isDrawerOpen: (state) => state.showDrawer,
  },

  actions: {
    toggle() {
      this.showDrawer = !this.showDrawer;
    },
    open() {
      this.showDrawer = true;
    },
    close() {
      this.showDrawer = false;
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useUIStore, import.meta.hot));
}
