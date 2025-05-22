<template>
  <q-drawer show-if-above side="right" :width="width" class="bg-white q-pb-md overflow-hidden">
    <q-separator class="q-mb-md" />
    <div class="q-mini-drawer-hide">
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

    <h2 class="text-h2">{{ mapStore.getSelectedRegionName }}</h2>
    <q-scroll-area class="full-height q-pa-md"> </q-scroll-area>
  </q-drawer>
</template>

<script setup lang="ts">
import { useMapStore } from 'src/stores/map';

const props = defineProps({
  width: String,
});

const mapStore = useMapStore();

const width = props.width ? parseInt(props.width) : 500;
</script>
