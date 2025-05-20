<template>
  <q-drawer
    v-model="ui.showDrawer"
    show-if-above
    side="right"
    :width="width"
    class="bg-white q-pb-md overflow-hidden"
  >
    <p>Drawer</p>
  </q-drawer>
</template>

<script setup lang="ts">
import { useUIStore } from '../stores/ui';

const ui = useUIStore();
const props = defineProps({
  width: String,
  show: Boolean,
});

const width = props.width ? parseInt(props.width) : 500;
</script>
