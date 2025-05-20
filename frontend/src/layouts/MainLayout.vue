<template>
  <q-layout view="lHh Lpr lFf">
    <MainHeader />

    <MainDrawer v-if="ui.showDrawer" :width="drawerWidth.toString()" />

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import MainDrawer from '../components/MainDrawer.vue';
import MainHeader from '../components/MainHeader.vue';
import { useUIStore } from '../stores/ui';

const ui = useUIStore();

const drawerWidth = ref(Math.max(Math.floor(window.innerWidth / 3), 500));
</script>
