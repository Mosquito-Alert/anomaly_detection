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
import { computed, ref } from 'vue';
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

const loading = computed(() => mapStore.fetchingRegionMetricSeasonality);
const data = computed(() => {
  const seasonality = mapStore.selectedRegionMetricSeasonality?.yearly || [];
  return seasonality.map((seasonalityItem: string, index: number) => ({
    date: new Date(2017, 0, index + 1), // Assuming index starts from 0 for January
    value: (Number(seasonalityItem) * 100).toFixed(2), // Convert to percentage
  }));
});

const option = computed(() => {
  return {
    title: {
      text: 'Seasonality component',
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
        return '<strong>' + params[0].name + '</strong>' + '<br />' + params[0].value;
      },
    },
    xAxis: {
      type: 'category',
      data: data.value.map((item: any) => date.formatDate(item.date, 'MMM')),
      axisLabel: {
        interval: 30, // Adjust this number to show fewer labels if needed
      },
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        data: data.value.map((item: any) => item),
        type: 'line',
        smooth: true,
        itemStyle: {
          color: getCssVar('accent'),
        },
      },
    ],
  };
});
</script>
