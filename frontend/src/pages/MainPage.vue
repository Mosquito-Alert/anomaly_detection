<template>
    <q-page>
      <AnomalyMap />
      <q-img style='z-index: 1' class='absolute-bottom q-mb-sm' position="calc(50% - 11px) center" fit='contain'
          src="~assets/logo_horizontal_black.png" height="30px" />
    </q-page>
  </template>

  <script setup lang="ts">
  import AnomalyMap from 'src/components/AnomalyMap.vue';
  </script>
