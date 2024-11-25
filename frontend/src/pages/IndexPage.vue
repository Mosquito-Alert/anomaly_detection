<template>
  <ol-map class="absolute-full" :loadTilesWhileAnimating="true" :loadTilesWhileInteracting="true">
    <ol-view ref="view" :center="center" :zoom="zoom" :constrainResolution="true" :maxZoom=17
      :projection="projection" />

    <ol-tile-layer>
      <ol-source-xyz :url="basemapLayerUrl" :preload="Infinity" :attributions-collapsible="false"
        attributions="© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap </a> contributors, © <a href='https://carto.com/about-carto'>Carto</a>" />
    </ol-tile-layer>

    <!-- <ol-interaction-select @select="featureSelected" :condition="selectCondition" :filter="selectInteractionFilter">
      <ol-style>
        <ol-style-stroke color="green" :width="10"></ol-style-stroke>
        <ol-style-fill color="rgba(255,255,255,0.5)"></ol-style-fill>
      </ol-style>
    </ol-interaction-select> -->

    <ol-vector-layer>
      <ol-source-vector :url="url" :format="geoJson" :projection="projection" />
      <ol-style :overrideStyleFunction="styleFn"></ol-style>
    </ol-vector-layer>

    <ol-tile-layer :z-index="10">
      <!-- <ol-source-osm :preload="Infinity" /> -->
      <ol-source-xyz :url="labelsLayerUrl" :preload="Infinity" :opaque="false" />
    </ol-tile-layer>

    <ol-interaction-select @select="featureHovered" :condition="hoverCondition" :filter="selectInteractionFilter">
      <!-- <ol-style>
        <ol-style-stroke color="green" :width="10"></ol-style-stroke>
        <ol-style-fill color="rgba(255,255,255,0.5)"></ol-style-fill>
      </ol-style> -->
    </ol-interaction-select>

  </ol-map>
</template>

<script setup>
import { ref, inject } from "vue";
import { Fill, Style } from "ol/style";
import { fromLonLat } from 'ol/proj.js'
import GeoJSON from 'ol/format/GeoJSON';

const basemapLayerUrl = ref("https://basemaps.cartocdn.com/rastertiles/light_nolabels/{z}/{x}/{y}.png");
const labelsLayerUrl = ref("https://basemaps.cartocdn.com/rastertiles/light_only_labels/{z}/{x}/{y}.png");

const projection = ref("EPSG:3857")
const center = ref(
  fromLonLat(
    [-3.6, 40.0],
    projection.value
  ),
);
const zoom = ref(7);

const url = ref("https://mapserver.mosquitoalert.com/geoserver/mosquitoalert/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=mosquitoalert%3Aspain_municipalities_anomaly_detection&srsName=EPSG:4326&outputFormat=application%2Fjson");
const geoJson = new GeoJSON();

const selectConditions = inject("ol-selectconditions");
const selectCondition = selectConditions.click;
const hoverCondition = selectConditions.pointerMove;

const featureSelected = (event) => {
  console.log(event);
};

const featureHovered = (event) => {
  console.log('hola');
  console.log(event);
};

const selectInteractionFilter = (feature, layer) => {
  return true
  return feature.values_.name != undefined;
};

function styleFn(feature) {
  const isAnomaly = feature.get('is_anomaly');
  const anomalyType = feature.get('anomaly_type');

  let fillColor;
  if (isAnomaly) {
    if (anomalyType === 'lower') {
      fillColor = '#007BFF'; // Blue for lower than expected
    } else if (anomalyType === 'higher') {
      fillColor = '#FF0000'; // Red for higher than expected
    } else {
      fillColor = '#808080'; // Grey for unspecified anomaly type (optional)
    }
  } else {
    fillColor = '#008000'; // Green for normal
  }

  return new Style({
    fill: new Fill({
      color: fillColor,
    }),
  });
}

</script>
