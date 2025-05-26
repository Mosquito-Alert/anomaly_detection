<template>
  <q-drawer show-if-above side="right" :width="width" class="bg-white q-pb-md overflow-hidden">
    <q-separator class="q-mb-md" />
    <div class="q-drawer-hide">
      <q-btn
        dense
        round
        unelevated
        color="accent"
        icon="chevron_right"
        @click="mapStore.clearSelectedFeatures"
      />
      Ocultar
      <!-- TODO: Improve (remove text, move it to the left so the icon is in the middle of the line) -->
    </div>

    <!-- * CONTENT -->
    <h2 class="text-h2 q-py-lg q-px-md q-ma-none">
      {{ title }}
    </h2>
    <q-separator class="q-mb-md" />
    <q-scroll-area class="full-height q-pa-md">
      <RegionSummary />
      <RegionAnomaliesHistoryTable />
      <RegionSeasonality style="background-color: rgb(255, 0, 0, 0.5); height: 500px" />
      <RegionAnomaliesChart style="background-color: rgb(0, 255, 0, 0.5)" />
    </q-scroll-area>
  </q-drawer>
</template>

<script setup lang="ts">
import { historyPageSize } from 'src/constants/config';
import { useMapStore } from 'src/stores/mapStore';
import { computed, onMounted, watch } from 'vue';

const props = defineProps({
  width: String,
});

const mapStore = useMapStore();

const updateDataHook = async () => {
  if (!mapStore.selectedRegionMetricId) return;
  await mapStore.fetchAndSetSelectedMetric(mapStore.selectedRegionMetricId!);
  await mapStore.fetchAndSetSelectedMetricHistory({ page: 1, pageSize: historyPageSize });
};

watch(
  () => mapStore.selectedRegionMetricId,
  async (newValue, oldValue) => {
    if (newValue !== oldValue) {
      await updateDataHook();
    }
  },
  { immediate: true },
);
onMounted(async () => {
  if (mapStore.selectedRegionMetricId) {
    await updateDataHook();
  }
});

const title = computed(() => {
  const defaultTitle = 'Region Unknown';
  const selectedRegionMetric = mapStore.selectedRegionMetric;
  if (!selectedRegionMetric) {
    return defaultTitle;
  }
  return `${selectedRegionMetric.region.name}, ${selectedRegionMetric.region.province}`;
});

// TODO: Define an action that fetched the next page

const width = props.width ? parseInt(props.width) : 500;
</script>
