<template>
  <div class="q-pa-sm q-my-sm rounded-borders bg-blue-grey-2">
    <div class="row q-pa-xs">
      <div class="col">
        <div class="row">
          <span class="text-weight-light">Vector Risk Index</span>
          <q-space />
          <!-- <q-badge :label="status" :color="statusColorName" v-if="!loadingFeature"></q-badge> -->
        </div>
        <div class="row justify-center">
          <!-- <span class="text-h1" v-if="!loadingFeature">{{ VRI }}%</span> -->
          <!-- <q-skeleton class="text-h1 full-width" v-if="loadingFeature" /> -->
        </div>
      </div>
      <q-separator vertical class="q-mx-md" />
      <div class="col">
        <div class="row">
          <span class="text-weight-light">Confidence levels</span>
        </div>
        <div class="row flex items-center justify-center">
          <span class="text-weight-light self-end">max.</span>
          <!-- <span class="text-h3" v-if="!loadingFeature">{{ upperBound }}%</span> -->
          <!-- <q-skeleton class="text-h3 col-4" v-if="loadingFeature" /> -->
        </div>
        <div class="row flex items-center justify-center">
          <span class="text-weight-light self-end">min.</span>
          <!-- <span class="text-h3" v-if="!loadingFeature">{{ lowerBound }}%</span> -->
          <!-- <q-skeleton class="text-h3 col-4" v-if="loadingFeature" /> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts"></script>
