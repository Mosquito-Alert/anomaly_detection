<template>
  <!-- TODO: AUTO FOCUS -->
  <q-select
    v-model="regionSelected"
    clearable
    autofocus
    use-input
    hide-selected
    fill-input
    input-debounce="250"
    label="Search by municipality"
    :options="suggestions"
    @filter="searchFilterFn"
    @filter-abort="abortFilterFn"
    @keydown.enter="selectFirstSuggestion"
    hide-dropdown-icon
    :style="searchbarStyle"
    class="q-ma-none q-py-none q-px-lg"
    bg-color="white"
    color="primary"
    label-color="black"
    standout="primary"
    outlined
    dense
  >
    <template v-slot:prepend>
      <q-icon color="black" name="place" />
    </template>
    <template v-slot:append>
      <q-icon
        color="black"
        v-if="!regionSelected"
        name="search"
        @click="selectFirstSuggestion"
        class="cursor-pointer"
      />
    </template>
    <template v-slot:no-option>
      <q-item>
        <q-item-section class="text-grey"> No results </q-item-section>
      </q-item>
    </template>
  </q-select>
</template>

<script setup lang="ts">
import { Metric } from 'anomaly-detection';
import { metricsApi, regionsApi } from 'src/services/apiService';
import { useMapStore } from 'src/stores/mapStore';
import { useUIStore } from 'src/stores/uiStore';
import { computed, ref, watch } from 'vue';

const uiStore = useUIStore();
const mapStore = useMapStore();

const suggestions = ref<{ label: string; value: string; id: number }[]>([]);
const regionSelected = ref<{ label: string; value: string; id: number } | null>(null);

const searchFilterFn = async (val: string, update: any, abort: any) => {
  if (val.length < 2) {
    abort();
    return;
  }
  update(async () => {
    try {
      const response = await regionsApi.list({
        regionName: val,
        pageSize: 5,
        ordering: 'name',
      });
      if (response.status === 200 && response.data.results) {
        suggestions.value = response.data.results.map((region: any) => ({
          label: `${region.name}, ${region.province}`,
          value: region.code,
          id: region.id,
        }));
      } else {
        throw new Error('Failed to fetch regions');
      }
    } catch (error) {
      console.error('Error fetching regions:', error);
      abort();
    }
  });
};
const selectFirstSuggestion = () => {
  if (suggestions.value.length > 0) {
    regionSelected.value = suggestions.value[0] as { label: string; value: string; id: number };
  }
};

const abortFilterFn = () => {
  suggestions.value = [];
};

const fetchMetricFromRegion = async (regionCode: string): Promise<Metric | null> => {
  if (!regionCode) return null;
  try {
    const response = await metricsApi.list({
      dateFrom: uiStore.date,
      dateTo: uiStore.date,
      regionCode,
    });
    if (response.status === 200 && response.data.results.length > 0) {
      const metric = response.data.results[0] as Metric;
      //   mapStore.selectedRegionMetricId = metric ? metric.id : '';
      return metric;
    } else {
      throw new Error('No metrics found for the selected region');
    }
  } catch (error) {
    console.error('Error fetching metric for region:', error);
    return null;
  }
};

watch(
  regionSelected,
  async (newValue) => {
    if (newValue && newValue.value) {
      const metric = await fetchMetricFromRegion(newValue.value);
      if (regionSelected.value && metric) {
        // Set the selected metric ID in the map store
        mapStore.selectedRegionMetricId = metric.id;
        await mapStore.fetchSelectedRegion(regionSelected.value.id);
        regionSelected.value = null; // Reset the selection after setting
        suggestions.value = []; // Clear suggestions after selection
      }
    }
  },
  { immediate: true },
);

const width = computed(() => uiStore.drawerWidth);

const searchbarStyle = computed(() => {
  return {
    width: `${width.value * 0.7}px`,
  };
});
</script>
<style lang="sass"></style>
