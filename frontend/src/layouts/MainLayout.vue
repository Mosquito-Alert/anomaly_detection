<template>
  <q-layout view="lHh Lpr lFf">

    <MainHeader />

    <MainDrawer :width="drawerWidth" />

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">

import { ref } from 'vue';

const drawerWidth = ref(Math.max(Math.floor(window.innerWidth / 3), 500))
</script>
