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

        <ol-vector-tile-layer ref="layerRef">
          <ol-source-vector-tile
            ref="sourceRef"
            :url="anomalyLayer.url"
            :format="anomalyLayer.format"
            :projection="projection"
            @featuresloadstart="handleSourceFeaturesLoadStart"
            @featuresloadend="handleSourceFeaturesLoadEnd"
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
import { fromLonLat } from 'ol/proj';
import { Fill, Style } from 'ol/style';
import { useQuasar } from 'quasar';
import { ANOMALY_COLORS } from 'src/constants/colors';
import { inject, ref } from 'vue';

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
const anomalyLayer = ref(
  {
    url: "/api/metrics/tiles/{z}/{x}/{y}/?date=2025-01-06",
    format: mvtFormat,
  }
)





const $q = useQuasar()
const handleSourceFeaturesLoadStart = () => {
  $q.loading.show({ 'message': 'Loading data...' })
}

const handleSourceFeaturesLoadEnd = () => {
  // features.value = event.features
  $q.loading.hide()
}


const styleFn = ()=> {
  return new Style({
    fill: new Fill({
      color: ANOMALY_COLORS.HIGH
    })
  })
}

</script>