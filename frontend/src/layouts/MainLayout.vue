<template>
  <q-layout view="lHh lpR lFf">
    <MainHeader />

    <RegionDetailedDrawer v-if="mapStore.isRegionSelected" />

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { useMapStore } from 'src/stores/mapStore';
import { useUIStore } from 'src/stores/uiStore';

const mapStore = useMapStore();
const uiStore = useUIStore();

uiStore.appWidth = window.innerWidth;
</script>
