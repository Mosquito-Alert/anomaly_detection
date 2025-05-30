<template>
  <q-input
    v-model="text"
    label="Search by municipality"
    class="q-ma-none q-py-none q-px-lg"
    outlined
    dense
    standout="primary"
    bg-color="white"
    color="primary"
    label-color="black"
    :style="searchbarStyle"
  >
    <template v-slot:prepend>
      <q-icon color="black" name="place" />
    </template>
    <template v-slot:append>
      <q-icon color="black" name="search" @click="text = 'TODO:'" class="cursor-pointer" />

      <q-icon v-if="text" name="close" @click="text = ''" class="cursor-pointer" />
    </template>
  </q-input>
</template>

<script setup lang="ts">
import { useUIStore } from 'src/stores/uiStore';
import { computed, ref } from 'vue';

const uiStore = useUIStore();

const width = computed(() => uiStore.drawerWidth);
const text = ref('');

const searchbarStyle = computed(() => {
  return {
    width: `${width.value}px`,
  };
});
</script>
<style lang="sass"></style>
