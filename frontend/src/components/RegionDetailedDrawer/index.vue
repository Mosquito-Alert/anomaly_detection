<template>
  <q-drawer show-if-above side="right" :width="width" class="bg-white overflow-hidden column">
    <div class="drawer-header">
      <q-separator class="q-mb-md" />
      <div class="q-drawer-hide">
        <q-btn
          dense
          round
          unelevated
          color="accent"
          icon="chevron_right"
          @click="() => mapStore.$reset()"
        />
        Ocultar
        <!-- TODO: Improve (remove text, move it to the left so the icon is in the middle of the line) -->
      </div>

      <h2 class="text-h2 q-py-lg q-px-md q-ma-none">
        {{ title }}
      </h2>
      <q-separator class="q-mb-md" />
    </div>
    <!-- * CONTENT -->
    <q-scroll-area class="drawer-content full-height q-px-md col overflow-auto">
      <RegionSummary />
      <RegionAnomaliesChart />
      <RegionModelInfo />
      <RegionAnomaliesHistoryTable />
    </q-scroll-area>
  </q-drawer>
</template>

<script setup lang="ts">
import { historyPageSize } from 'src/constants/config';
import { useMapStore } from 'src/stores/mapStore';
import { useUIStore } from 'src/stores/uiStore';
import { computed, onMounted, watch } from 'vue';

const uiStore = useUIStore();
const mapStore = useMapStore();

const updateDataHook = async () => {
  if (!mapStore.selectedRegionMetricId) return;
  await mapStore.fetchAndSetSelectedMetric(mapStore.selectedRegionMetricId!);
  await mapStore.fetchAndSetSelectedMetricSeasonality();
  await mapStore.fetchAndSetSelectedMetricAll();
  await mapStore.fetchAndSetSelectedMetricTrend();
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

const width = computed(() => Math.max(Math.floor(uiStore.appWidth / 2.75), 500));
</script>
