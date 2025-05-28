<template>
  <q-option-group
    name="chart_shown"
    v-model="chart_shown"
    :options="options"
    color="primary"
    inline
  />
  <div class="bg-white rounded-borders">
    <v-chart
      v-if="chart_shown === options[0]?.value"
      style="height: 250px"
      :option="option"
      :loading="loading"
    />
    <v-chart
      v-if="chart_shown === options[1]?.value"
      style="height: 250px"
      :option="optionTrend"
      :loading="loading"
    />
  </div>
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
const uiStore = useUIStore();

const loading = computed(() => mapStore.fetchingRegionMetricSeasonality);
const data = computed(() => {
  const seasonality = mapStore.selectedRegionMetricSeasonality?.yearly || [];
  return seasonality.map((seasonalityItem: string, index: number) => ({
    date: new Date(2017, 0, index + 1), // Assuming index starts from 0 for January
    value: (Number(seasonalityItem) * 100).toFixed(2), // Convert to percentage
  }));
});
const trendDate = computed((): Date => {
  return mapStore.selectedRegionMetricTrend?.date
    ? new Date(mapStore.selectedRegionMetricTrend.date)
    : new Date(uiStore.date); // Default to the data date if no trend date is available
});
const trend = computed(() => {
  const data = mapStore.selectedRegionMetricTrend?.trend || [];
  // Map each trend value with a date given the last date in the trend
  return data.map((item: string, index: number): { date: Date; value: number } => {
    // Number of days until the trend date given the index of the current trend value
    const daysUntilTrendDate = trend?.value?.length - 1 - index;
    // Calculate the date for each trend value
    const date = new Date(trendDate.value);
    date.setDate(date.getDate() - daysUntilTrendDate);
    return { date, value: Number(item) * 100 };
  });
});

const chart_shown = ref('seasonality');
const options = ref([
  { label: 'Seasonality', value: 'seasonality' },
  { label: 'Trend', value: 'trend' },
]);

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

const optionTrend = computed(() => {
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
