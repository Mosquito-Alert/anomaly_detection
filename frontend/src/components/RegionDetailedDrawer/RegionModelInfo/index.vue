<template>
  <q-btn
    outline
    color="primary"
    label="Review Model components"
    class="q-ma-lg"
    @click="showModelComponents = true"
  />

  <q-dialog v-model="showModelComponents">
    <q-card id="model-info-dialog">
      <q-card-section
        v-touch-pan.mouse="onPan"
        id="model-info-dialog-header"
        class="row items-center q-pb-sm"
      >
        <span class="text-h5 q-px-md">Model components</span>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-card-section class="q-pa-lg">
        <p>
          The model components are used to understand the underlying patterns in the data.
          Currently, there are two components available:
        </p>
        <ul>
          <li><strong>Seasonality</strong> of the bites index over the year.</li>
          <li><strong>Trend</strong> of the bites index over time.</li>
        </ul>
        <q-icon name="lightbulb" color="primary" size="1.5rem" class="q-ma-xs q-mr-sm" />
        <span>TIP: You can drag the dialog to reposition it.</span>

        <q-option-group
          name="chart_shown"
          v-model="chart_shown"
          :options="options"
          color="primary"
          inline
        />
        <div class="bg-white rounded-borders">
          <RegionSeasonality v-if="chart_shown === options[0]?.value" />
          <RegionTrend v-if="chart_shown === options[1]?.value" />
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { useUIStore } from 'src/stores/uiStore';
import { computed, ref } from 'vue';
// TODO: Persistent, dragable

const showModelComponents = ref(false);
const coordinates = ref({ x: 0, y: 0 });

const chart_shown = ref('seasonality');
const options = ref([
  { label: 'Seasonality', value: 'seasonality' },
  { label: 'Trend', value: 'trend' },
]);

const uiStore = useUIStore();
const width = uiStore.appWidth * 0.5; // 50% of the app width
const transform = computed(() => `translate(${coordinates.value.x}px, ${coordinates.value.y}px)`);

const onPan = (event: any) => {
  coordinates.value.x += event.delta.x;
  coordinates.value.y += event.delta.y;
  console.log(coordinates.value);
};
</script>
<style scoped lang="scss">
#model-info-dialog {
  max-width: v-bind(width);
  transform: v-bind(transform);
}

#model-info-dialog-header {
  cursor: move;
  background-color: #fdf7e6;
}
</style>
