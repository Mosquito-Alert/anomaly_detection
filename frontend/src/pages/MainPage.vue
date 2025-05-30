<template>
  <q-page>
    <!-- MAP -->
    <AnomalyMap v-if="dateFetched" :date="uiStore.date" />

    <!-- SEARCH BAR -->
    <q-page-sticky position="top-left" :offset="[0, 20]">
      <SearchBox v-if="!mapStore.selectedRegionMetricId" />
    </q-page-sticky>

    <!-- DATE -->
    <q-page-sticky position="top-right" :offset="[20, 20]">
      <span
        class="q-px-md q-py-xs text-weight-medium text-subtitle1"
        id="map-date"
        v-if="!uiStore.fetchingDate"
      >
        {{ uiStore.formattedDate }}
      </span>
      <q-skeleton type="QBadge" v-if="uiStore.fetchingDate" />
    </q-page-sticky>

    <!-- LOGO -->
    <q-img
      style="z-index: 1"
      class="absolute-bottom q-mb-sm"
      position="calc(50% - 11px) center"
      fit="contain"
      src="~assets/logo_horizontal_black.png"
      height="2.5rem"
    />
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import { useMapStore } from 'src/stores/mapStore';
import { useUIStore } from 'src/stores/uiStore';
import { onMounted, ref } from 'vue';

const $q = useQuasar();

const uiStore = useUIStore();
const mapStore = useMapStore();

const dateFetched = ref(false);

// * Lifecycle
onMounted(async () => {
  $q.loading.show({ message: 'Loading data...' });
  await uiStore.fetchLastDate();
  dateFetched.value = true;
  $q.loading.hide();
});
</script>
<style lang="scss">
.ol-zoom {
  top: auto !important;
  bottom: 5em !important;
  left: auto !important;
  right: 1em !important;

  button {
    width: 1.75em !important;
    height: 1.75em !important;
  }
}
.ol-scale-line {
  top: auto !important;
  bottom: 2em !important;
  left: auto !important;
  right: 1em !important;
}
</style>
