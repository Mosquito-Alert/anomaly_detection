<template>
  <q-layout view="lHh lpR lFf">
    <MainHeader v-if="!mapStore.isRegionSelected" />

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
uiStore.drawerWidth = Math.max(Math.floor(uiStore.appWidth / 2.75), 500);
</script>
