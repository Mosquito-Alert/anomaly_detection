<template>
  <q-drawer show-if-above side="right" :width="width" class="bg-white q-pb-md overflow-hidden">
    <!-- Button that closes the drawer -->
    <q-btn class="q-mb-md" icon="close" round dense flat @click="mapStore.clearSelectedFeatures">
      Close drawer
    </q-btn>
    <p>{{ mapStore.getSelectedRegionName }}</p>
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
