<template>
  <v-chart style="height: 250px" :option="option" :loading="features.length === 0" class="rounded-borders" />
</template>

<script>

import { computed } from "vue"
import { ANOMALY_COLORS } from "src/constants/colors"

import VChart from "vue-echarts"

import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([TooltipComponent, LegendComponent, PieChart, CanvasRenderer])


export default {
  components: {
    VChart
  },
  props: {
    features: {
      type: Array,
    }
  },
  setup(props) {
    const data = computed(() => {
      return props.features.reduce((acc, feature) => {
        let anomaly = feature.get('anomaly'); // Get the 'anomaly_type' property

        let anomalyType;
        if (anomaly === 0) {
          anomalyType = 'usual';
        } else if (anomaly === 1) {
          anomalyType = 'higher';
        } else if (anomaly === -1) {
          anomalyType = 'lower';
        } else {
          anomalyType = 'unknown'; // Optional: Handle unexpected cases
        }

        // Initialize the count if not already initialized
        if (!acc[anomalyType]) {
          acc[anomalyType] = 0;
        }

        // Increment the count for the anomalyType
        acc[anomalyType]++;

        return acc;
      }, {}); // Initialize the accumulator as an empty object
    });

    const option = computed(() => {
      return {
        title: {
          text: 'Summary',
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
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          right: '1>0%',
          top: 'center'
        },
        series: [
          {
            name: 'Anomaly type',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            labelLine: {
              show: false
            },
            data: [
              { value: data.value['usual'] || 0, name: 'Usual', itemStyle: { color: ANOMALY_COLORS.USUAL } },
              { value: data.value['lower'] || 0, name: 'Lower', itemStyle: { color: ANOMALY_COLORS.LOW } },
              { value: data.value['higher'] || 0, name: 'Higher', itemStyle: { color: ANOMALY_COLORS.HIGH } },
            ]
          }
        ]
      }
    })

    return {
      option
    };
  }
}

</script>

<style lang="scss" scope></style>
