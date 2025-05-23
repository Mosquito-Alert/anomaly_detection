<template>
  <q-page>
    <ol-map
      ref="mapRef"
      class="absolute-full"
      :loadTilesWhileAnimating="true"
      :loadTilesWhileInteracting="true"
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

      <ol-vector-layer :z-index="10">
        <ol-source-vector :features="selectedFeatures" />
        <ol-style :overrideStyleFunction="selectedStyleFn"></ol-style>
      </ol-vector-layer>

      <ol-tile-layer :z-index="15">
        <ol-source-xyz
          :url="labelsLayer.url"
          :preload="labelsLayer.preload"
          :opaque="labelsLayer.opaque"
        />
      </ol-tile-layer>

      <ol-fullscreen-control />
      <ol-scaleline-control />
    </ol-map>
  </q-page>
</template>

<script setup lang="ts">
import { Feature, MapBrowserEvent } from 'ol';
import { fromLonLat } from 'ol/proj';
import { Fill, Stroke, Style } from 'ol/style';
import type MapRef from 'ol/Map';
// import Tooltip from 'ol-ext/overlay/Tooltip';
import { getCssVar, useQuasar } from 'quasar';
import { ANOMALY_COLORS } from 'src/constants/colors';
import { computed, inject, ref, watchEffect } from 'vue';
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

const selectedFeatures = ref([] as FeatureLike[]);

const mapRef = ref<{ map: MapRef } | null>(null);
const viewRef = ref();
const sourceRef = ref(null);
const layerRef = ref(null);

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
const mvtFormat = new format.MVT({ idProperty: 'id' });
const anomalyLayer = computed(() => {
  return {
    url: `/api/metrics/tiles/{z}/{x}/{y}/?date=${props.date}`,
    format: mvtFormat,
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
  selectedFeatures.value = [firstFeature];
  await mapStore.fetchAndSetSelectedMetric(firstFeature.getId() as string);

  // DELETE:
  console.log(`Selected metric:`, mapStore.selectedRegionMetric);
};
// Zoom to selectedFeature
watchEffect(() => {
  if (mapStore.isRegionSelected) {
    const feature = selectedFeatures.value[0] as FeatureLike;
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
  if (anomaly_degree !== 0) {
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
  const style = hoverStyleFn(feature);
  (style.getStroke() as Stroke).setWidth(4);
  return style;
};

const hoverStyleFn = (feature: any) => {
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
