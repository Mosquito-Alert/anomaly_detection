<template>
  <ol-map
    ref="mapRef"
    class="absolute-full"
    @click="selectFeature"
    :loadTilesWhileAnimating="true"
    :loadTilesWhileInteracting="true"
  >
    <ol-view
      ref="viewRef"
      :center="center"
      :zoom="zoom"
      :maxZoom="maxZoom"
      :projection="projection"
    />
    <ol-vector-tile-layer ref="layerRef" class-name="feature-layer">
      <ol-source-vector-tile
        ref="sourceRef"
        :url="'/api/metrics/tiles/{z}/{x}/{y}/?date=2025-01-06'"
        :format="mvtFormat"
        :projection="projection"
      />
      <ol-style>
        <ol-style-stroke color="#fff" :width="0.3" />
        <ol-style-fill color="#ff8899" :opacity="0.5" />
      </ol-style>
    </ol-vector-tile-layer>

    <ol-vector-layer :z-index="15">
      <ol-source-vector :features="selectedFeatures" />
      <ol-style>
        <ol-style-fill color="#00ff00" :opacity="0.5" />
      </ol-style>
    </ol-vector-layer>
  </ol-map>
</template>

<script setup lang="ts">
import { Feature, MapBrowserEvent } from 'ol';
import { fromLonLat } from 'ol/proj';
import type MapRef from 'ol/Map';
import { ref, inject } from 'vue';
import { FeatureLike } from 'ol/Feature';
import { Layer } from 'ol/layer';

const mapRef = ref<{ map: MapRef } | null>(null);
const viewRef = ref(null);
const sourceRef = ref(null);
const layerRef = ref(null);

// * Base config
const projection = ref('EPSG:3857');
const center = ref(fromLonLat([-3.6, 40.0], projection.value));
const zoom = ref(7);
const maxZoom = ref(17);

const format = inject('ol-format');
const mvtFormat = new format.MVT({
  idProperty: 'region__code',
});

// Hover and select features
const selectedFeatures = ref<FeatureLike[]>([]);

function layerFilter(layerCandidate: Layer) {
  return layerCandidate.getClassName().includes('feature-layer');
}
/**
 * select feature
 */
function selectFeature(event: MapBrowserEvent<PointerEvent>) {
  const map = mapRef.value?.map;
  if (!map) {
    return;
  }

  // store selected feature
  const features = map.getFeaturesAtPixel(event.pixel, {
    hitTolerance: 0,
    layerFilter,
  });
  if (!features.length) {
    return;
  }
  // So only one feature is selected
  const firstFeature = features[0] as Feature;
  selectedFeatures.value = [firstFeature];
  console.log(
    `Selected feature (${firstFeature.getId()}) properties:`,
    firstFeature.getProperties(),
  );
}
</script>
