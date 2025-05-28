<template>
  <q-card flat bordered id="model-info-card-button" class="q-my-lg q-mx-md">
    <q-card-section horizontal @click="showModelComponents = true">
      <q-card-section class="icon-query-open">
        <!-- Color background icon, border rounded -->
        <q-icon name="keyboard_arrow_left" size="3rem" class="" />
      </q-card-section>
      <q-card-section>
        <div class="text-h6">Review Model components</div>
        <span>Useful to understand the underlying patterns in the data.</span>
      </q-card-section>
      <q-card-section>
        <!-- Color background icon, border rounded -->
        <q-icon name="query_stats" color="primary" size="3rem" />
      </q-card-section>
    </q-card-section>
  </q-card>

  <!-- DIALOG -->
  <q-dialog v-model="showModelComponents">
    <q-card id="model-info-dialog" :style="{ transform: transform, width: width, maxWidth: width }">
      <q-card-section
        v-touch-pan.mouse="onPan"
        id="model-info-dialog-header"
        class="row items-center q-pb-sm"
      >
        <span class="text-h5 q-px-md">Model components</span>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section class="q-pa-none">
        <q-tabs v-model="tab" id="model-info-tab" align="justify" narrow-indicator>
          <q-tab name="seasonality" label="Seasonality" />
          <q-tab name="trend" label="Trend" />
          <q-tab name="info" label="Info" />
        </q-tabs>

        <q-tab-panels v-model="tab" animated class="q-px-lg">
          <q-tab-panel name="seasonality">
            <RegionSeasonality />
          </q-tab-panel>

          <q-tab-panel name="trend">
            <RegionTrend />
          </q-tab-panel>

          <q-tab-panel name="info">
            <p>Currently, there are two components available:</p>
            <ul>
              <li><strong>Seasonality</strong> of the bites index over the year.</li>
              <li><strong>Trend</strong> of the bites index over time.</li>
            </ul>
            <q-icon name="lightbulb" color="primary" size="1.5rem" class="q-ma-xs q-mr-sm" />
            <span>TIP: You can drag the dialog to reposition it.</span>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { useUIStore } from 'src/stores/uiStore';
import { computed, ref } from 'vue';

const uiStore = useUIStore();

const showModelComponents = ref(false);
const tab = ref('seasonality');
const width = computed(() => `${uiStore.appWidth * 0.5}px` || '500px');
const coordinates = ref({ x: 0, y: 0 });
const transform = computed(() => `translate(${coordinates.value.x}px, ${coordinates.value.y}px)`);

const onPan = (event: any) => {
  coordinates.value.x += event.delta.x;
  coordinates.value.y += event.delta.y;
  console.log(coordinates.value);
};
</script>
<style scoped lang="scss">
#model-info-card-button {
  cursor: pointer;
  background-color: #fdf7e6;
  //   background-color: #f9e7b5;
  .icon-query-open {
    background-color: #f3c954;
    //   background-color: #f9e7b5;
  }
}
#model-info-dialog-header {
  cursor: move;
  background-color: #fdf7e6;
  //   background-color: #f9e7b5;
}

#model-info-tab {
  //   background-color: #fdf7e6;
  background-color: #f9e7b5;
}
</style>
