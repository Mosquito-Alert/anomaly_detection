import { defineStore, acceptHMRUpdate } from 'pinia';

export const useUIStore = defineStore('uiStore', {
  state: () => ({
    date: '2025-01-01',
  }),

  getters: {
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
    // * Date
    setDate(newDate: string) {
      this.date = newDate;
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useUIStore, import.meta.hot));
}
