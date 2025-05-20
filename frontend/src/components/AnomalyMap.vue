<template>
    <q-page>
        <ol-map
        ref="mapRef"
        class="absolute-full"
        :loadTilesWhileAnimating="true"
        :loadTilesWhileInteracting="true"
        >
        <ol-view
            ref="view"
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
            attributions="basemapLayer.attributions"
          />
        </ol-tile-layer>

        <ol-vector-tile-layer
          v-if="!dateFetched"
          ref="layerRef"
          :renderMode="'vector'"
        >
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

        <ol-tile-layer :z-index="10">
          <ol-source-xyz
            :url="labelsLayer.url"
            :preload="labelsLayer.preload"
            :opaque="labelsLayer.opaque"
            />
        </ol-tile-layer>

        </ol-map>
    </q-page>
</template>

<script setup lang="ts">
import { Feature } from 'ol';
import { fromLonLat } from 'ol/proj';
import { Fill, Style } from 'ol/style';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';
import { ANOMALY_COLORS } from 'src/constants/colors';
import { computed, inject, onMounted, ref } from 'vue';

const date = ref("2025-01-01");
const dateFetched = ref(true);

// * Base config
const projection = ref('EPSG:3857');
const center = ref(
  fromLonLat(
    [-3.6, 40.0],
    projection.value
  ),
);
const zoom = ref(7);
const maxZoom = ref(17);

// * Map layers
const basemapLayer = ref({
  url: "https://basemaps.cartocdn.com/rastertiles/light_nolabels/{z}/{x}/{y}.png",
  attributions: "© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap </a> contributors, © <a href='https://carto.com/about-carto'>Carto</a>",
  attributionsCollapsible: false,
  preload: Infinity,
})
const labelsLayer = ref(
  {
    url: "https://basemaps.cartocdn.com/rastertiles/light_only_labels/{z}/{x}/{y}.png",
    preload: Infinity,
    opaque: false,
  }
)
const format = inject("ol-format");
const mvtFormat = new format.MVT();
const anomalyLayer = computed(() => {
  return {
    show: date.value !== null,
    url: `/api/metrics/tiles/{z}/{x}/{y}/?date=${date.value}`,
    format: mvtFormat,
  }
})


// * Lifecycle
onMounted(async () => {
  try {
    $q.loading.show({ 'message': 'Loading data...' })
    const res = await api.get('/metrics/dates/last/')
    date.value = res?.data?.date || date.value;
    anomalyLayer.value.show = date.value !== null;
  } catch (error) {
    console.error('Error fetching latest date:', error);
  } finally {
    dateFetched.value = false;
    $q.loading.hide();
  }
})


const $q = useQuasar()
const handleSourceTileLoadStart = () => {
  $q.loading.show({ 'message': 'Loading data...' })
}
const handleSourceTileLoadEnd = () => {
  $q.loading.hide()
}


function styleFn(feature: Feature) {

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
    })
  });
}

</script>