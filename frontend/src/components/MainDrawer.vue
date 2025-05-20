<template>
  <q-drawer show-if-above side="right" :width="width" class="bg-white q-pb-md overflow-hidden">
    <p>Drawer</p>
  </q-drawer>
</template>

<script setup lang="ts">
const props = defineProps({
  width: String,
});

const width = props.width ? parseInt(props.width) : 500;
</script>
