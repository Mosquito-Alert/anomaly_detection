<template>
  <q-page>
    <AnomalyMap v-if="dateFetched" :date="ui.date" />
    <q-img
      style="z-index: 1"
      class="absolute-bottom q-mb-sm"
      position="calc(50% - 11px) center"
      fit="contain"
      src="~assets/logo_horizontal_black.png"
      height="30px"
    />
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';
import AnomalyMap from 'src/components/AnomalyMap.vue';
import { useUIStore } from 'src/stores/ui';
import { onMounted, ref } from 'vue';

const $q = useQuasar();

const ui = useUIStore();

const dateFetched = ref(false);

// * Lifecycle
onMounted(async () => {
  try {
    $q.loading.show({ message: 'Loading data...' });
    const res = await api.get('/metrics/dates/last/');
    ui.setDate(res?.data?.date || ui.date);
    dateFetched.value = true;
  } catch (error) {
    console.error('Error fetching latest date:', error);
  } finally {
    $q.loading.hide();
  }
});
</script>
