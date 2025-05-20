import { defineStore, acceptHMRUpdate } from 'pinia';

export const useUIStore = defineStore('myStore', {
  state: () => ({
    showDrawer: false,
    date: '2025-01-01',
  }),

  getters: {
    isDrawerOpen: (state) => state.showDrawer,
    formattedDate: (state) => {
      const date = new Date(state.date);
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      });
    },
  },

  actions: {
    // * Drawer
    toggleDrawer() {
      this.showDrawer = !this.showDrawer;
    },
    openDrawer() {
      this.showDrawer = true;
    },
    closeDrawer() {
      this.showDrawer = false;
    },
    // * Date
    setDate(newDate: string) {
      this.date = newDate;
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useUIStore, import.meta.hot));
}
