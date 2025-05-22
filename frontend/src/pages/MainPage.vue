<template>
  <q-page>
    <AnomalyMap v-if="dateFetched" :date="uiStore.date" />
    <q-img
      style="z-index: 1"
      class="absolute-bottom q-mb-sm"
      position="calc(50% - 11px) center"
      fit="contain"
      src="~assets/logo_horizontal_black.png"
      height="30px"
    />
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import { useUIStore } from 'src/stores/uiStore';
import { onMounted, ref } from 'vue';

const $q = useQuasar();

const uiStore = useUIStore();

const dateFetched = ref(false);

// * Lifecycle
onMounted(async () => {
  $q.loading.show({ message: 'Loading data...' });
  await uiStore.fetchLastDate();
  dateFetched.value = true;
  $q.loading.hide();
});
</script>
