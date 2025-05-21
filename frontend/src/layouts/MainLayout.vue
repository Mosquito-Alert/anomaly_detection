<template>
  <q-layout view="lHh Lpr lFf">
    <MainHeader />

    <MainDrawer v-if="mapStore.isRegionSelected" :width="drawerWidth.toString()" />

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import MainDrawer from '../components/MainDrawer.vue';
import MainHeader from '../components/MainHeader.vue';
import { useMapStore } from 'src/stores/map';

const mapStore = useMapStore();

const drawerWidth = ref(Math.max(Math.floor(window.innerWidth / 3), 500));
</script>
