<template>
  <div class="bg-white rounded-borders">
    <v-chart style="height: 250px" :option="option" :loading="!featureId" />
  </div>
</template>

<script>
import { date, getCssVar } from 'quasar'
import { computed, ref, watch } from "vue"

import VChart from "vue-echarts"

import { use } from 'echarts/core'
import { LineChart, ScatterChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, DataZoomComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'


use([TooltipComponent, LineChart, ScatterChart, CanvasRenderer, GridComponent, TitleComponent, DataZoomComponent])

export default {
  components: {
    VChart
  },
  props: {
    featureId: {
      type: String,
      required: true
    }
  },
  setup(props) {

    const seasonalityData = ref([]);
    const loading = ref(false)

    const fetchSeasonalityFeatureData = async () => {
      try {
        loading.value = true
        const baseUrl = 'https://mapserver.mosquitoalert.com/geoserver/mosquitoalert/ows'
        const params = new URLSearchParams({
          service: 'WFS',
          version: '2.0.0',
          request: 'GetFeature',
          typeName: 'mosquitoalert:anomaly_seasonality_bites',
          outputFormat: 'application/json',
          viewparams: `feature_id:${props.featureId.split('.')[1]};`
        });
        const response = await fetch(`${baseUrl}?${params}`);
        const data = await response.json();

        seasonalityData.value = data.features.map(
          item => ({
            date: new Date(2017, 0, item.properties.index + 1),
            value: (Number(item.properties.yearly) * 100).toFixed(2)
          })
        )
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        loading.value = false
      }
    };

    watch(() => props.featureId, () => {
      fetchSeasonalityFeatureData()
    }, { immediate: true })

    const option = computed(() => {
      return {
        title: {
          text: 'Seasonality component',
          left: 'left',
          top: 'top',
          textStyle: {
            fontFamily: 'Roboto', // Set the font family
            fontSize: 20,         // Adjust font size as needed
            fontWeight: '400',   // Optional: make it bold
            color: '#333'         // Optional: customize the color
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: function (params) {
            return (
              '<strong>' + params[0].name + '</strong>' +
              '<br />' +
              params[0].value
            );
          }
        },
        xAxis: {
          type: 'category',
          data: seasonalityData.value.map(function (item) {
            return date.formatDate(item.date, 'MMM');
          }),
          axisLabel: {
            interval: 30,  // Adjust this number to show fewer labels if needed
          },
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: seasonalityData.value.map(function (item) {
              return item.value;
            }),
            type: 'line',
            smooth: true,
            itemStyle: {
              color: getCssVar('accent')
            },
          }
        ]
      };
    })

    return {
      option
    }
  }
}

</script>
