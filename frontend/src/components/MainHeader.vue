<template>
  <q-header class="bg-white text-black">
    <q-toolbar>
      <q-avatar square>
        <img src="~assets/logo.png" />
      </q-avatar>
      <q-toolbar-title class="text-h4">Anomaly Detection / Spain</q-toolbar-title>

      <span class="text-grey" v-if="ui.formattedDate"> {{ ui.formattedDate }}</span>
      <q-skeleton type="QBadge" v-if="ui.formattedDate === undefined" />
    </q-toolbar>
  </q-header>
</template>

<script setup lang="ts">
import { useUIStore } from 'src/stores/ui';

const ui = useUIStore();
</script>
