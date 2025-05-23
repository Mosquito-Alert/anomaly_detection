<template>
  <div class="q-pa-sm q-my-sm rounded-borders bg-blue-grey-2">
    <div class="row q-pa-xs">
      <div class="col">
        <div class="row">
          <span class="text-weight-light">Bites Index</span>
          <q-space />
          <q-badge :label="status" :color="statusColorName" v-if="!loading"></q-badge>
        </div>
        <!-- TODO: (For the 3 values): change font size relative to the width so the info is well framed  -->
        <div class="row justify-center">
          <span class="text-h1" v-if="!loading">{{ metric.value }}%</span>
          <q-skeleton class="text-h1 full-width" v-if="loading" />
        </div>
      </div>
      <q-separator vertical class="q-mx-md" />
      <div class="col">
        <div class="row">
          <span class="text-weight-light">Confidence levels</span>
        </div>
        <div class="row flex items-center justify-center">
          <span class="text-weight-light self-end">max.</span>
          <span class="text-h3" v-if="!loading">{{ metric.upper_value }}%</span>
          <q-skeleton class="text-h3 col-4" v-if="loading" />
        </div>
        <div class="row flex items-center justify-center">
          <span class="text-weight-light self-end">min.</span>
          <span class="text-h3" v-if="!loading">{{ metric.lower_value }}%</span>
          <q-skeleton class="text-h3 col-4" v-if="loading" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { MetricDetail } from 'anomaly-detection';
import { useMapStore } from 'src/stores/mapStore';

const mapStore = useMapStore();

const metric = computed<MetricDetail>(() => mapStore.getFormattedRegionMetric as MetricDetail);
const loading = computed(() => mapStore.fetchingRegionMetric);

const status = computed(() => {
  if (
    Object.keys(metric).length === 0 ||
    metric.value.anomaly_degree === undefined ||
    metric.value.anomaly_degree === null
  ) {
    return;
  }

  let resultText;

  if (metric.value.anomaly_degree > 0) {
    resultText = 'High';
  } else if (metric.value.anomaly_degree < 0) {
    resultText = 'Low';
  } else if (metric.value.anomaly_degree === 0) {
    resultText = 'Usual';
    console.log('ASDASDASD');
  } else {
    resultText = 'N/A';
  }

  return resultText;
});
const statusColorName = computed(() => {
  let color;
  switch (status.value || '') {
    case 'Usual':
      color = 'anomaly-usual'; // From app.scss
      break;
    case 'Low':
      color = 'anomaly-lower'; // From app.scss
      break;
    case 'High':
      color = 'anomaly-higher'; // From app.scss
      break;
    default:
      color = 'gray'; // Default color if no match
  }
  return color;
});
</script>
