<template>
  <q-drawer
    show-if-above
    side="right"
    :width="width"
    class="bg-white q-pb-md q-px-md overflow-hidden"
  >
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
    <h2 class="text-h2 q-py-lg q-ma-none">
      {{ title }}
    </h2>
    <q-separator class="q-mb-md" />
    <RegionSummary
      :metric="mapStore.getFormattedRegionMetric"
      :loading="mapStore.fetchingRegionMetric"
    />
    <RegionSeasonality style="background-color: rgb(255, 0, 0, 0.5)" />
    <RegionAnomaliesChart style="background-color: rgb(0, 255, 0, 0.5)" />
    <RegionAnomaliesTable style="background-color: rgb(0, 0, 255, 0.5)" />

    <q-scroll-area class="full-height q-pa-md"> </q-scroll-area>
  </q-drawer>
</template>

<script setup lang="ts">
import { useMapStore } from 'src/stores/mapStore';
import { computed } from 'vue';

const props = defineProps({
  width: String,
});

const mapStore = useMapStore();

const title = computed(() => {
  const defaultTitle = 'Region Unknown';
  const selectedRegionMetric = mapStore.selectedRegionMetric;
  if (!selectedRegionMetric) {
    return defaultTitle;
  }
  return `${selectedRegionMetric.region.name}, ${selectedRegionMetric.region.province}`;
});

const width = props.width ? parseInt(props.width) : 500;
</script>
