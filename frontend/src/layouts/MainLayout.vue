<template>
  <q-layout view="lHh Lpr lFf">
    <MainHeader />

    <RegionDetailedDrawer v-if="mapStore.isRegionSelected" :width="drawerWidth.toString()" />

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useMapStore } from 'src/stores/mapStore';

const mapStore = useMapStore();

const drawerWidth = ref(Math.max(Math.floor(window.innerWidth / 3), 500));
</script>
