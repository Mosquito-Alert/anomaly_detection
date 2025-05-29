<template>
  <q-drawer show-if-above side="left" :width="width" class="bg-white overflow-hidden column">
    <div class="drawer-header q-pt-lg q-pb-sm q-px-lg q-ma-none" style="background-color: #f9e7b5">
      <q-btn
        dense
        flat
        icon="close"
        size="0.85rem"
        class="q-drawer-hide absolute"
        style="top: 1rem; right: 1rem"
        @click="() => mapStore.$reset()"
      />
      <p class="text-h3 q-ma-none q-mb-xs">
        {{ municipalityName }}
      </p>
      <div class="row q-mb-sm">
        <div class="col-10">
          <p class="text-h6 text-weight-regular" style="color: #333">{{ provinceName }}</p>
          <p class="text-subtitle-1 text-weight-regular q-ma-none" style="color: #333">
            {{ uiStore.formattedDate }}
          </p>
        </div>
        <div class="col self-end">
          <span>Bites Index</span>
          <q-badge
            :label="status"
            :color="statusColorName"
            class="q-py-sm q-px-md q-mt-xs"
            v-if="!loading"
          ></q-badge>
        </div>
      </div>
    </div>
    <q-separator class="q-mb-md" />
    <!-- * CONTENT -->
    <q-scroll-area class="drawer-content full-height q-px-md col overflow-auto">
      <RegionAnomaliesChart />
      <RegionSeasonality />
      <RegionSummary />
      <RegionAnomaliesHistoryTable />
    </q-scroll-area>
  </q-drawer>
</template>

<script setup lang="ts">
import { MetricDetail } from 'anomaly-detection';
import { historyPageSize } from 'src/constants/config';
import { useMapStore } from 'src/stores/mapStore';
import { useUIStore } from 'src/stores/uiStore';
import {
  AnomalyClassificationEnum,
  anomalyClassificationStyle,
  classifyAnomaly,
} from 'src/utils/anomalyClassification';
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

const metric = computed<MetricDetail>(() => mapStore.getFormattedRegionMetric as MetricDetail);
const loading = computed(() => mapStore.fetchingRegionMetric);

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

const municipalityName = computed(() => {
  const defaultTitle = 'Municipality Unknown';
  const selectedRegionMetric = mapStore.selectedRegionMetric;
  if (!selectedRegionMetric) {
    return defaultTitle;
  }
  return selectedRegionMetric.region.name;
});
const provinceName = computed(() => {
  const defaultTitle = 'Province Unknown';
  const selectedRegionMetric = mapStore.selectedRegionMetric;
  if (!selectedRegionMetric) {
    return defaultTitle;
  }
  return selectedRegionMetric.region.province;
});

const status = computed(() => {
  if (
    Object.keys(metric).length === 0 ||
    metric.value.anomaly_degree === undefined ||
    metric.value.anomaly_degree === null
  ) {
    return;
  }

  return classifyAnomaly(metric.value.anomaly_degree) as AnomalyClassificationEnum;
});
const statusColorName = computed(() => {
  return anomalyClassificationStyle(status.value || AnomalyClassificationEnum.N_A);
});

const width = computed(() => Math.max(Math.floor(uiStore.appWidth / 2.75), 500));
</script>
