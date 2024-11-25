<template>
  <q-layout view="lHr lpR lFr">
    <q-drawer show-if-above side="left" :width="drawerWidth" class="bg-white q-py-md overflow-hidden">
      <q-select v-model="selectedMunicipality" @update:model-value="updateSelection" :options="filteredOptions"
        hide-bottom-space clearable autofocus :use-input="!selectedFeature" input-debounce="20" input-class="text-h2"
        input-style="min-height: 3.75rem" @filter="searchFilterFn" :placeholder="selectedFeature ? '' : 'Spain'"
        class="q-pb-none q-mx-md">
        <template v-slot:selected>
          <span class="text-h2">{{ selectedFeature ? selectedMunicipality.label : '' }}</span>
        </template>
      </q-select>

      <q-scroll-area class="full-height q-pa-md">
        <SummaryPieChart :features="features" v-show="!selectedFeatureId" />
        <CcaaChart :last-date="lastUpdateDate" v-show="!selectedFeatureId" />
        <MunicipalityDetail :feature-id="selectedFeatureId" v-if="selectedFeatureId" />

        <div class="row text-weight-thin justify-center items-center q-pt-md q-pb-sm">
          <span>Last update: {{ lastUpdateFormattedDate }}</span>
          <q-skeleton type='QBadge' v-if="lastUpdateFormattedDate === undefined" />
          <q-btn flat round color='primary' icon='o_info' type='a' size="sm" @click="infoToolbar = true" />
        </div>
      </q-scroll-area>

      <q-dialog v-model="infoToolbar">
        <q-card>
          <q-toolbar>
            <q-toolbar-title><span class="text-weight-bold">Anomaly Detection</span></q-toolbar-title>

            <q-btn flat round dense icon="close" v-close-popup />
          </q-toolbar>

          <q-card-section class="text-weight-regular text-justify">
            The <strong>Anomaly Detection Dashboard</strong> lets you monitor mosquito activity across municipalities
            based
            on predicted mosquito probabilities.
            Simply click on any municipality to access detailed information, trends, and historical data for that
            area.
            The current mosquito probability is color-coded to help you quickly identify anomalies, indicating whether
            it is
            <strong><span style="color: blue;">lower</span></strong>, <strong><span
                style="color: green;">normal</span></strong>, or <strong><span
                style="color: red;">higher</span></strong>
            than usual for this time of year.
          </q-card-section>
        </q-card>
      </q-dialog>

    </q-drawer>

    <q-page-container>
      <q-page>
        <ol-map ref="mapRef" class="absolute-full" :loadTilesWhileAnimating="true" :loadTilesWhileInteracting="true">
          <ol-view ref="viewRef" :center="center" :zoom="zoom" :constrainResolution="true" :maxZoom=17
            :projection="projection" />

          <ol-tile-layer>
            <ol-source-xyz ref="sourceRef" :url="basemapLayerUrl" :preload="Infinity" :attributions-collapsible="false"
              attributions="© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap </a> contributors, © <a href='https://carto.com/about-carto'>Carto</a>" />
          </ol-tile-layer>

          <ol-vector-layer ref="layerRef">
            <ol-source-vector ref="sourceRef" :url="wfsUrl" :format="geoJson" :projection="projection"
              @featuresloadstart="handleSourceFeaturesLoadStart" @featuresloadend="handleSourceFeaturesLoadEnd" />
            <ol-style :overrideStyleFunction="styleFn"></ol-style>
          </ol-vector-layer>

          <ol-tile-layer :z-index="10">
            <ol-source-xyz :url="labelsLayerUrl" :preload="Infinity" :opaque="false" />
          </ol-tile-layer>

          <ol-interaction-select @select="featureHovered" :condition="hoverCondition" :filter="selectInteractionFilter">
            <ol-style :overrideStyleFunction="hoverStyleFn"></ol-style>
          </ol-interaction-select>
          <ol-interaction-select @select="featureSelected" :condition="selectCondition"
            :filter="selectInteractionFilter">
            <ol-style :overrideStyleFunction="selectedStyleFn"></ol-style>
          </ol-interaction-select>

          <ol-fullscreen-control />
          <ol-scaleline-control />

        </ol-map>
        <q-img style='z-index: 1' class='absolute-bottom q-mb-sm' position="calc(50% - 11px) center" fit='contain'
          src="/img/logo_horizontal_black.png" height="30px" />

      </q-page>
    </q-page-container>

  </q-layout>
</template>

<script setup>

import { useQuasar, getCssVar } from 'quasar'
import { date } from 'quasar';
import { ANOMALY_COLORS } from 'src/constants/colors'

import { ref, inject, computed, watchEffect, onMounted, watch } from "vue";
import { Fill, Style, Stroke } from "ol/style";
import { fromLonLat } from 'ol/proj.js'
import GeoJSON from 'ol/format/GeoJSON';

import Tooltip from 'ol-ext/overlay/Tooltip';

import CcaaChart from 'src/components/CcaaChart.vue';
import SummaryPieChart from "src/components/SummaryPieChart.vue";
import MunicipalityDetail from "src/components/MunicipalityDetail.vue";

const $q = useQuasar()

// Left Drawer
const drawerWidth = ref(Math.max(Math.floor(window.innerWidth / 3), 500))
const lastUpdateDate = computed(() => {
  if (features.value.length === 0) {
    return
  }
  return new Date(features.value[0]?.get('last_update'))
})
const lastUpdateFormattedDate = computed(() => {
  let formattedDate;
  if (lastUpdateDate.value) {
    formattedDate = date.formatDate(lastUpdateDate.value, 'YYYY-MM-DD')
  }
  return formattedDate
})
const infoToolbar = ref(false)

// Map
const mapRef = ref()
const viewRef = ref()
const layerRef = ref()
const sourceRef = ref()
const basemapLayerUrl = ref("https://basemaps.cartocdn.com/rastertiles/light_nolabels/{z}/{x}/{y}.png");
const labelsLayerUrl = ref("https://basemaps.cartocdn.com/rastertiles/light_only_labels/{z}/{x}/{y}.png");
const wfsUrl = ref("https://mapserver.mosquitoalert.com/geoserver/mosquitoalert/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=mosquitoalert%3Aspain_municipalities_anomaly_detection&srsName=EPSG:4326&outputFormat=application%2Fjson");
const geoJson = new GeoJSON();

const features = ref([]);
const projection = ref("EPSG:3857")
const center = ref(
  fromLonLat(
    [-3.6, 40.0],
    projection.value
  ),
);
const zoom = ref(7);

const selectConditions = inject("ol-selectconditions");
const selectCondition = selectConditions.click;
const featureSelected = (event) => {
  selectedFeature.value = event.selected[0]
};
const hoverCondition = selectConditions.pointerMove;
const featureHovered = (event) => {
  if (event.selected.length === 0) {
    hoverTooltip.removeFeature()
  } else {
    hoverTooltip.setFeature(event.selected[0])
  }
};
const selectInteractionFilter = (feature, layer) => {
  // Only take layerRef into account
  return layer === layerRef.value.vectorLayer
};

const hoverTooltip = new Tooltip({
  getHTML: (feature, info) => {
    if (feature) {
      return feature.get('NAMEUNIT')
    }
  },
  positioning: 'bottom-center'
});

const handleSourceFeaturesLoadStart = (event) => {
  $q.loading.show({ 'message': 'Loading data...' })
}

const handleSourceFeaturesLoadEnd = (event) => {
  features.value = event.features
  $q.loading.hide()
}

onMounted(() => {
  mapRef.value.map.addOverlay(hoverTooltip)
})


function updateSelection(value) {
  if (value) {
    selectedFeature.value = features.value.find(item => item.getId() === value.id)
  } else {
    selectedFeature.value = null
  }
}
const selectedMunicipality = ref()




const selectedFeature = ref()
watch(selectedFeature, (newValue, oldValue) => {
  if (oldValue) {
    oldValue.setStyle(styleFn);
  }
  if (newValue) {
    newValue.setStyle(selectedStyleFn);
  }
})
const selectedFeatureId = computed(() => {
  return selectedFeature.value?.getId()
})
// Zoom to selectedFeature
watchEffect(() => {
  if (selectedFeature.value) {
    viewRef.value.view.fit(selectedFeature.value.getGeometry().getExtent(), {
      padding: [50, 50, 50, 50], //Padding around the feature
      duration: 1000 // duration of the zoom animation in milliseconds
    });
  }
})


const filteredOptions = ref([]);
const selectOptions = computed(() => {
  return features.value.map(feature => {
    return {
      id: feature.getId(),
      label: feature.get('NAMEUNIT') + ', ' + feature.get('NAMEUNIT_NUT2'), // Get the NAMEUNIT property
      searchValue: feature.get('NAMEUNIT'),
      value: feature.getId()  // Get the NUTCODE property
    };
  }).sort((a, b) => a.label.localeCompare(b.label));
})
watchEffect(() => {
  if (selectedFeature.value) {
    selectedMunicipality.value = selectOptions.value.find(item => item.id === selectedFeature.value.getId())
  }
})

function searchFilterFn(val, update, abort) {
  if (val.length < 2) {
    abort()
    return
  }

  update(() => {
    // Function to remove accents and normalize the strings
    const normalize = (str) =>
      str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

    const needle = normalize(val.trim());

    filteredOptions.value = selectOptions.value.filter(v =>
      normalize(v.searchValue).includes(needle)
    ).sort((a, b) => {
      const normalizedA = normalize(a.searchValue);
      const normalizedB = normalize(b.searchValue);
      // Prioritize results where the needle matches the start of the string
      const aStartsWith = normalizedA.startsWith(needle) ? 0 : 1;
      const bStartsWith = normalizedB.startsWith(needle) ? 0 : 1;
      // Sort by start match first, then alphabetically
      return aStartsWith - bStartsWith || normalizedA.localeCompare(normalizedB);
    });
  })
}

function styleFn(feature) {

  let fillColor;

  switch (feature.get('anomaly')) {
    case 1:
      fillColor = ANOMALY_COLORS.HIGH;
      break;
    case -1:
      fillColor = ANOMALY_COLORS.LOW;
      break;
    case 0:
      fillColor = ANOMALY_COLORS.USUAL_LIGHT + '48'; // with alpha 0.7
      break;
    default:
      fillColor = '#808080';
  }

  return new Style({
    fill: new Fill({
      color: fillColor,
    })
  });
}

function hoverStyleFn(feature) {
  const style = styleFn(feature)

  style.setStroke(
    new Stroke({
      color: getCssVar('accent'),
      width: 2
    })
  )
  return style
}

function selectedStyleFn(feature) {
  const style = hoverStyleFn(feature)
  style.getStroke().setWidth(4)
  return style
}

</script>


<style lang="scss">
.q-textarea {
  .q-field__native {
    line-height: 3.75rem; // From text-h2
  }
}

.q-field__marginal {
  height: unset;
}

.ol-popup {
  margin-top: 30x;
}
</style>
