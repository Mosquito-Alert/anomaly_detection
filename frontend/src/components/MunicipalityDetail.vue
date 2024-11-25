<template>
  <div class="q-pa-sm q-my-sm rounded-borders bg-blue-grey-2">
    <div class="row q-pa-xs">
      <div class="col">
        <div class="row">
          <span class="text-weight-light">Vector Risk Index</span>
          <q-space />
          <q-badge :label="status" :color="statusColorName" v-if="!loadingFeature"></q-badge>
        </div>
        <div class="row justify-center">
          <span class="text-h1" v-if="!loadingFeature">{{ VRI }}%</span>
          <q-skeleton class="text-h1 full-width" v-if="loadingFeature" />
        </div>
      </div>
      <q-separator vertical class="q-mx-md" />
      <div class="col">
        <div class="row">
          <span class="text-weight-light">Confidence levels</span>
        </div>
        <div class="row flex items-center justify-center">
          <span class="text-weight-light self-end">max.</span>
          <span class="text-h3" v-if="!loadingFeature">{{ upperBound }}%</span>
          <q-skeleton class="text-h3 col-4" v-if="loadingFeature" />
        </div>
        <div class="row flex items-center justify-center">
          <span class="text-weight-light  self-end">min.</span>
          <span class="text-h3" v-if="!loadingFeature">{{ lowerBound }}%</span>
          <q-skeleton class="text-h3 col-4" v-if="loadingFeature" />
        </div>
      </div>
    </div>
  </div>


  <MunicipalitySeasonalityLineChart :feature-id="featureId" v-if="featureId" />
  <AnomaliesChart :data="historyData" :loading="loadingHistory" class="q-mt-sm" />
  <AnomalyTable :data="anomalyData" :loading="loadingHistory" />


</template>

<script>

import { ref, computed, watch } from 'vue';

import AnomaliesChart from './AnomaliesLineChart.vue';
import AnomalyTable from './AnomalyTable.vue';
import MunicipalitySeasonalityLineChart from './MunicipalitySeasonalityLineChart.vue';

export default {
  components: {
    AnomaliesChart,
    AnomalyTable,
    MunicipalitySeasonalityLineChart
  },
  props: {
    featureId: {
      type: String,
      required: true
    },
  },
  setup(props) {
    const loadingHistory = ref(false)
    const loadingFeature = ref(false)

    const featureData = ref()
    const VRI = computed(() => {
      return (featureData.value?.y * 100).toFixed(1)
    })
    const lowerBound = computed(() => {
      let result = (featureData.value?.yhat_lower * 100).toFixed(1);
      if (result == 0) {
        // Avoid negative zeros -0.0
        result = '0'
      }
      return result
    })
    const upperBound = computed(() => {
      let result = (featureData.value?.yhat_upper * 100).toFixed(1);
      if (result == 0) {
        // Avoid negative zeros -0.0
        result = '0'
      }
      return result
    })
    const status = computed(() => {
      if (featureData.value === undefined) {
        return
      }

      let resultText;

      switch (featureData.value.anomaly) {
        case 1:
          resultText = 'High';
          break;
        case -1:
          resultText = 'Low';
          break;
        case 0:
          resultText = 'Usual';
          break;
        default:
          resultText = 'N/A';
      }
      return resultText
    })
    const statusColorName = computed(() => {
      let color;
      switch (status.value || '') {
        case "Usual":
          color = 'anomaly-usual';  // From app.scss
          break;
        case "Low":
          color = 'anomaly-lower';  // From app.scss
          break;
        case "High":
          color = 'anomaly-higher';  // From app.scss
          break;
        default:
          color = "gray"; // Default color if no match
      }
      return color
    })

    const historyData = ref([])

    const anomalyData = computed(() => {
      return historyData.value.filter(item => item.anomaly !== 0)
    })

    const fetchFeatureData = async () => {
      featureData.value = undefined;
      try {
        loadingFeature.value = true
        const baseUrl = 'https://mapserver.mosquitoalert.com/geoserver/mosquitoalert/ows'
        const params = new URLSearchParams({
          service: 'WFS',
          version: '2.0.0',
          request: 'GetFeature',
          typeName: 'mosquitoalert:spain_municipalities_anomaly_detection',
          outputFormat: 'application/json',
          featureID: props.featureId
        });
        const response = await fetch(`${baseUrl}?${params}`);
        const data = await response.json();

        featureData.value = data.features[0]?.properties
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        loadingFeature.value = false
      }
    };

    const fetchHistoryData = async () => {
      historyData.value = []
      try {
        loadingHistory.value = true
        const baseUrl = 'https://mapserver.mosquitoalert.com/geoserver/mosquitoalert/ows'
        const params = new URLSearchParams({
          service: 'WFS',
          version: '2.0.0',
          request: 'GetFeature',
          typeName: 'mosquitoalert:anomaly_detection_histories',
          outputFormat: 'application/json',
          viewparams: `feature_id:${props.featureId.split('.')[1]};`
        });
        const response = await fetch(`${baseUrl}?${params}`);
        const data = await response.json();

        historyData.value = data.features.map(
          item => ({
            date: new Date(item.properties.ds),
            y: (item.properties.y * 100),
            yhat: (item.properties.yhat * 100),
            yhat_lower: (item.properties.yhat_lower * 100),
            yhat_upper: (item.properties.yhat_upper * 100),
            trend: (item.properties.trend * 100),
            anomaly: Number(item.properties.anomaly),
            importance: Number(item.properties.importance)
          })
        )
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        loadingHistory.value = false
      }
    };

    watch(() => props.featureId, () => {
      fetchFeatureData();
      fetchHistoryData();
    }, { immediate: true })

    return {
      loadingHistory,
      loadingFeature,
      VRI,
      lowerBound,
      upperBound,
      status,
      statusColorName,
      historyData,
      anomalyData
    }
  }
}

</script>
