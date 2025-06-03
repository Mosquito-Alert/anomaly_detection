<template>
  <q-page>
    <ol-map
      ref="mapRef"
      class="absolute-full"
      :loadTilesWhileAnimating="true"
      :loadTilesWhileInteracting="true"
      @pointermove="hoverFeature"
      @click="selectFeature"
    >
      <ol-view
        ref="viewRef"
        :center="center"
        :zoom="zoom"
        :maxZoom="maxZoom"
        :projection="projection"
      />

      <ol-tile-layer>
        <ol-source-xyz
          ref="sourceRef"
          :url="basemapLayer.url"
          :preload="basemapLayer.preload"
          :attributions-collapsible="basemapLayer.attributionsCollapsible"
          :attributions="basemapLayer.attributions"
        />
      </ol-tile-layer>

      <ol-vector-tile-layer ref="layerRef" class-name="feature-layer">
        <ol-source-vector-tile
          ref="sourceRef"
          :url="anomalyLayer.url"
          :format="anomalyLayer.format"
          :projection="projection"
          @tileloadstart="handleSourceTileLoadStart"
          @tileloadend="handleSourceTileLoadEnd"
        />
        <ol-style :overrideStyleFunction="styleFn"></ol-style>
      </ol-vector-tile-layer>

      <ol-vector-layer :z-index="9" render-mode="vector">
        <ol-source-vector :features="hoveredFeatures" />
        <ol-style :overrideStyleFunction="hoveredStyleFn"></ol-style>
      </ol-vector-layer>

      <ol-vector-layer :z-index="10" render-mode="vector">
        <ol-source-vector :features="mapStore.selectedFeatures" />
        <ol-style :overrideStyleFunction="selectedStyleFn"></ol-style>
      </ol-vector-layer>

      <ol-tile-layer :z-index="15">
        <ol-source-xyz
          :url="labelsLayer.url"
          :preload="labelsLayer.preload"
          :opaque="labelsLayer.opaque"
        />
      </ol-tile-layer>

      <ol-zoom-control />
      <ol-scaleline-control />
    </ol-map>
  </q-page>
</template>

<script setup lang="ts">
import { Feature, MapBrowserEvent, Overlay } from 'ol';
import { fromLonLat } from 'ol/proj';
import { Fill, Stroke, Style } from 'ol/style';
import type MapRef from 'ol/Map';
import { getCssVar, useQuasar } from 'quasar';
import { ANOMALY_COLORS } from 'src/constants/colors';
import { computed, inject, onMounted, ref, watchEffect } from 'vue';
import { Layer } from 'ol/layer';
import { useMapStore } from 'src/stores/mapStore';
import { FeatureLike } from 'ol/Feature';
import { Geometry } from 'ol/geom';

const props = defineProps({
  date: {
    type: String,
    required: true,
  },
});
const mapStore = useMapStore();

const hoveredFeatures = ref([] as FeatureLike[]);

const mapRef = ref<{ map: MapRef } | null>(null);
const viewRef = ref();
const sourceRef = ref(null);
const layerRef = ref(null);

onMounted(() => {
  const map = mapRef.value?.map;
  if (!map) {
    return;
  }
  // map.addOverlay(hoverTooltip);

  map.addOverlay(hoverOverlay);
});

const $q = useQuasar();

/**
 * Base config
 */
const projection = ref('EPSG:3857');
const center = ref(fromLonLat([-3.6, 40.0], projection.value));
const zoom = ref(7);
const maxZoom = ref(17);

// * Map layers
const basemapLayer = ref({
  url: 'https://basemaps.cartocdn.com/rastertiles/light_nolabels/{z}/{x}/{y}.png',
  attributions:
    "© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap </a> contributors, © <a href='https://carto.com/about-carto'>Carto</a>",
  attributionsCollapsible: false,
  preload: Infinity,
});
const labelsLayer = ref({
  url: 'https://basemaps.cartocdn.com/rastertiles/light_only_labels/{z}/{x}/{y}.png',
  preload: Infinity,
  opaque: false,
});
const format = inject('ol-format');
const MVTFormat = new format.MVT({ idProperty: 'id' });
const anomalyLayer = computed(() => {
  return {
    url: `/api/metrics/tiles/{z}/{x}/{y}/?date=${props.date}`,
    format: MVTFormat,
  };
});

const handleSourceTileLoadStart = () => {
  $q.loading.show({ message: 'Loading data...' });
};
const handleSourceTileLoadEnd = () => {
  $q.loading.hide();
};

/**
 * Select and hover features
 */
const layerFilter = (layerCandidate: Layer) => {
  return layerCandidate.getClassName().includes('feature-layer');
};

const selectFeature = async (event: MapBrowserEvent<PointerEvent>) => {
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
  mapStore.selectedFeatures = [firstFeature];
  mapStore.selectedRegionMetricId = firstFeature.getId() as string;
};

const tooltipEl = document.createElement('div');
tooltipEl.className = 'custom-tooltip';
const hoverOverlay = new Overlay({
  element: tooltipEl,
  offset: [-15, -5],
  positioning: 'bottom-left',
});

const hoverFeature = async (event: MapBrowserEvent<PointerEvent>) => {
  const map = mapRef.value?.map;
  if (!map) {
    return;
  }

  // store hovered feature
  const features = map.getFeaturesAtPixel(event.pixel, {
    hitTolerance: 0,
    layerFilter,
  });
  if (!features.length) {
    hoveredFeatures.value = [];
    // hoverTooltip.removeFeature();
    tooltipEl.classList.remove('visible');
    hoverOverlay.setPosition(undefined); // hide
    return;
  }
  hoveredFeatures.value = features as Feature[];
  const feature = features[0] as FeatureLike;
  tooltipEl.innerHTML = feature.get('region__name');
  tooltipEl.classList.add('visible');
  hoverOverlay.setPosition(event.coordinate);
};

// Zoom to selectedFeature
watchEffect(() => {
  if (mapStore.isRegionSelected && mapStore.selectedFeatures.length > 0) {
    const feature = mapStore.selectedFeatures[0] as FeatureLike;
    const geometry = feature.getGeometry() as Geometry;
    viewRef.value.view.fit(geometry.getExtent(), {
      padding: [250, 250, 250, 250], //Padding around the feature
      duration: 600, // duration of the zoom animation in milliseconds
    });
  }
  // # TODO: Zoom out if selected feature is cleared
});

/**
 * Styles
 */
const styleFn = (feature: Feature) => {
  // TODO: Add a gradient to the fill color based on the anomaly degree
  let fillColor;
  const anomaly_degree = feature.get('anomaly_degree');
  if (anomaly_degree && anomaly_degree !== 0) {
    fillColor = anomaly_degree > 0 ? ANOMALY_COLORS.HIGH : ANOMALY_COLORS.LOW;
  } else {
    fillColor = ANOMALY_COLORS.USUAL_LIGHT + '48'; // with alpha 0.7
  }

  return new Style({
    fill: new Fill({
      color: fillColor,
    }),
  });
};

const selectedStyleFn = (feature: any) => {
  const style = hoveredStyleFn(feature);
  (style.getStroke() as Stroke).setWidth(4);
  return style;
};

const hoveredStyleFn = (feature: any) => {
  const style = styleFn(feature);

  style.setStroke(
    new Stroke({
      color: getCssVar('accent') || '#FF0000',
      width: 2,
    }),
  );
  return style;
};
</script>
<style lang="scss">
#map-date {
  background-color: #f3c954;
  color: #444;
  border-radius: 4px;
  border: 1px solid #edb20c;
}
.custom-tooltip {
  position: relative; /* Needed for the arrow positioning */
  background-color: rgba(0, 0, 0, 0.75); /* dark with transparency */
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  font-size: 0.85rem;
  white-space: nowrap;
  pointer-events: none;
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
  opacity: 0;
  transform: scale(0.95);
}

.custom-tooltip.visible {
  opacity: 1;
  transform: scale(1);
}

/* Add a triangle pointer */
.custom-tooltip::after {
  content: '';
  position: absolute;
  bottom: -6px; /* position below the tooltip */
  left: 10px; /* adjust to align with cursor or center */
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid rgba(0, 0, 0, 0.75); /* same as tooltip background */
}
</style>
