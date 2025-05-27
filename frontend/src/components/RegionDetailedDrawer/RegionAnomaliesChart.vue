<template>
  <div class="bg-white rounded-borders">
    <v-chart style="height: 250px" :option="option" :loading="loading" />
  </div>
</template>

<script setup lang="ts">
import VChart from 'vue-echarts';
import { date, getCssVar } from 'quasar';
import { useMapStore } from 'src/stores/mapStore';
import { computed } from 'vue';
import { use } from 'echarts/core';
import {
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, ScatterChart } from 'echarts/charts';
import { ANOMALY_COLORS } from 'src/constants/colors';
import { Metric } from 'anomaly-detection';

const mapStore = useMapStore();
use([
  TooltipComponent,
  LineChart,
  ScatterChart,
  CanvasRenderer,
  GridComponent,
  TitleComponent,
  LegendComponent,
  DataZoomComponent,
]);

const loading = computed(() => mapStore.fetchingRegionMetricsAll);
const data = computed(() => mapStore.selectedRegionMetricsAll?.results || []);

const option = computed(() => {
  return {
    title: {
      text: 'Bites index time series',
      left: 'left',
      top: 'top',
      textStyle: {
        fontFamily: 'Roboto', // Set the font family
        fontSize: 20, // Adjust font size as needed
        fontWeight: '400', // Optional: make it bold
        color: '#333', // Optional: customize the color
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        animation: false,
        label: {
          backgroundColor: '#ccc',
          borderColor: '#aaa',
          borderWidth: 1,
          shadowBlur: 0,
          shadowOffsetX: 0,
          shadowOffsetY: 0,
          color: '#222',
        },
      },
      formatter: (params: any) => {
        const date = params[0].name || 'Unknown Date';
        const value = params[0].value ? `${(params[0].value * 100).toFixed(2)}%` : 'N/A';
        const lowerBound = params[1].value ? `${(params[1].value * 100).toFixed(2)}%` : 'N/A';
        const upperBound =
          params[1].value && params[2].value
            ? `${((params[1].value + params[2].value) * 100).toFixed(2)}%`
            : 'N/A';
        return `
          <strong>${date}</strong>
          <br/><hr>
          <span>Value: ${value}</span><br/>
          <span>Lower bound: ${lowerBound}</span><br/>
          <span>Upper bound: ${upperBound}</span><br/>
        `;
      },
    },
    legend: {
      data: ['Actuals', 'Forecast'],
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: data.value.map((item) => {
        return date.formatDate(item.date, 'YYYY-MM-DD');
      }),
      boundaryGap: false,
    },
    yAxis: {
      // min: 0, // Sets the minimum value to 0
      axisLabel: {
        formatter: (val: any) => {
          return (val * 100).toFixed(0) + '%'; // Converts fractions to percentages
        },
      },
      axisPointer: {
        label: {
          formatter: (params: any) => {
            return params.value.toFixed(2) + '%'; // Converts fractions to percentages
          },
        },
      },
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
      },
      {
        type: 'inside',
        xAxisIndex: [0],
      },
    ],
    series: [
      {
        name: 'Actuals',
        type: 'scatter',
        symbolSize: function (value: any, params: any) {
          return 4;
          // return Math.pow(params.data.anomaly_degree || 1, 2) * 10; // Adjust size based on anomaly degree
        },
        itemStyle: {
          color: '#909090',
        },
        data: data.value.map((item: Metric) => {
          return {
            value: (item.value || 0) * 1.0,
            anomalyDegree: item.anomaly_degree,
            itemStyle: {
              color:
                item.anomaly_degree === null || item.anomaly_degree === 0
                  ? '#909090'
                  : item.anomaly_degree > 0
                    ? ANOMALY_COLORS.HIGH
                    : ANOMALY_COLORS.LOW,
            },
          };
        }),
        showSymbol: false,
      },
      {
        name: 'Uncertainty interval lower bound',
        type: 'line',
        data: data.value.map((item) => {
          return item.lower_value;
        }),
        lineStyle: {
          opacity: 0,
        },
        stack: 'confidence-band',
        symbol: 'none',
      },
      {
        name: 'Uncertainty interval area',
        type: 'line',
        data: data.value.map((item) => {
          return (item.upper_value || 0) - (item.lower_value || 0);
        }),
        lineStyle: {
          opacity: 0,
        },
        areaStyle: {
          color: 'rgba(237, 178, 12, 0.3)',
        },
        stack: 'confidence-band',
        symbol: 'none',
      },
      {
        name: 'Forecast',
        type: 'line',
        data: data.value.map((item) => {
          return (item.predicted_value || 0) * 1.0;
        }),
        itemStyle: {
          color: 'rgba(237, 178, 12, 0.5)',
        },
        showSymbol: false,
      },
    ],
  };
});
</script>
