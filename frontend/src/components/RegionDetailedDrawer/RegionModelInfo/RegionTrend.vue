<template>
  <v-chart style="height: 250px" :option="option" :loading="loading" />
</template>

<script setup lang="ts">
import { LineChart, ScatterChart } from 'echarts/charts';
import {
  DataZoomComponent,
  GridComponent,
  TitleComponent,
  TooltipComponent,
} from 'echarts/components';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { date, getCssVar } from 'quasar';
import { useMapStore } from 'src/stores/mapStore';
import { useUIStore } from 'src/stores/uiStore';
import { trendDataCorrection } from 'src/utils/trendDataCorrection';
import { computed } from 'vue';
import VChart from 'vue-echarts';

use([
  TooltipComponent,
  LineChart,
  ScatterChart,
  CanvasRenderer,
  GridComponent,
  TitleComponent,
  DataZoomComponent,
]);

const mapStore = useMapStore();
const uiStore = useUIStore();

const loading = computed(() => mapStore.fetchingRegionMetricTrend);
const trendDate = computed((): Date => {
  return mapStore.selectedRegionMetricTrend?.date
    ? new Date(mapStore.selectedRegionMetricTrend.date)
    : new Date(uiStore.date); // Default to the data date if no trend date is available
});
const trend = computed(() => {
  const data = mapStore.selectedRegionMetricTrend?.trend || [];
  return trendDataCorrection(data, trendDate.value);
});

const option = computed(() => {
  return {
    title: {
      text: 'Trend component',
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
      formatter: (params: any) => {
        return `
            <strong>${params[0].name}</strong>
            <br/><hr>
            <span>Value: ${params[0].value.toFixed(2)}%</span><br/>
          `;
      },
    },
    xAxis: {
      type: 'category',
      data: trend.value.map((item) => date.formatDate(item.date, 'YYYY-MM-DD')),
      boundaryGap: false,
    },
    yAxis: {
      axisLabel: {
        formatter: (val: number) => val.toFixed(0) + '%', // Converts fractions to percentages
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
        name: 'Trend',
        type: 'line',
        data: trend.value.map((item) => item.value * 1.0),
        itemStyle: {
          color: getCssVar('accent'),
        },
        showSymbol: false,
      },
    ],
  };
});
</script>
