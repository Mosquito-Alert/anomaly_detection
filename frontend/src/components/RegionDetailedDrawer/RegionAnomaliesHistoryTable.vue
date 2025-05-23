<template>
  <p>Table</p>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { PaginatedMetricList } from 'anomaly-detection';
import { useMapStore } from 'src/stores/mapStore';

const mapStore = useMapStore();

const history = computed<PaginatedMetricList>(
  () => mapStore.selectedRegionHistory as PaginatedMetricList,
);
</script>
