<template>
  <div class="bg-white rounded-borders">
    <h6 class="q-my-sm q-ml-sm text-weight-regular" style="color: #333">Time Series</h6>
    <!-- TODO: Button to show/conceal points that aren't anomalies -->
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
import { trendDataCorrection } from 'src/utils/trendDataCorrection';
import { useUIStore } from 'src/stores/uiStore';

const uiStore = useUIStore();
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

const anomaliesLoading = computed(() => mapStore.fetchingRegionMetricsAll);
const anomaliesData = computed(() => mapStore.selectedRegionMetricsAll?.results || []);
const trendLoading = computed(() => mapStore.fetchingRegionMetricTrend);
const trendDate = computed((): Date => {
  return mapStore.selectedRegionMetricTrend?.date
    ? new Date(mapStore.selectedRegionMetricTrend.date)
    : new Date(uiStore.date); // Default to the data date if no trend date is available
});
const trend = computed(() => {
  const data = mapStore.selectedRegionMetricTrend?.trend || [];
  return trendDataCorrection(data, trendDate.value);
});
const loading = computed(() => anomaliesLoading.value || trendLoading.value);
const percentageLastMonth = computed(() => {
  return 100 - (30 / anomaliesData.value.length) * 100; // Assuming the last month has 30 days
});

const option = computed(() => {
  return {
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
        const date = params[0]?.name || 'Unknown Date';
        const value = params[0]?.value ? `${params[0].value.toFixed(2)}%` : 'N/A';
        const lowerBound = params[1]?.value ? `${params[1].value.toFixed(2)}%` : 'N/A';
        const upperBound =
          params[1].value && params[2]?.value
            ? `${(params[1].value + params[2].value).toFixed(2)}%`
            : 'N/A';
        const trend = params[4]?.value ? `${params[4].value.toFixed(2)}%` : 'N/A';
        // TODO: Conditionally show forecast and trend depending if they are disabled or not in the UI
        return `
          <strong>${date}</strong>
          <br/><hr>
          <span>Value: ${value}</span><br/>
          <span>Lower bound: ${lowerBound}</span><br/>
          <span>Upper bound: ${upperBound}</span><br/>
          <span>Trend: ${trend}</span><br/>
        `;
      },
    },
    legend: {
      // TODO: Trend to Interannual Trend
      data: ['Actuals', 'Forecast', 'Trend'],
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: anomaliesData.value.map((item) => date.formatDate(item.date, 'YYYY-MM-DD')),
      boundaryGap: false,
    },
    yAxis: {
      // min: 0, // Sets the minimum value to 0
      axisLabel: {
        formatter: (val: any) => val.toFixed(0) + '%', // Converts fractions to percentages
      },
      axisPointer: {
        label: {
          formatter: (params: any) => params.value.toFixed(2) + '%', // Converts fractions to percentages
        },
      },
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: percentageLastMonth.value,
        end: 100,
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
        symbolSize: (value: any, params: any) => {
          const minSize = 4; // Minimum size for the symbol
          const maxSize = 20; // Maximum size for the symbol
          const anomalyDegree = params.data.anomalyDegree || 0;
          if (anomalyDegree === 0) return minSize; // Return minimum size for non-anomalous points
          return minSize + Math.abs(anomalyDegree) * (maxSize - minSize);
        }, // Adjust size based on anomaly degree
        itemStyle: {
          color: '#909090',
        },
        data: anomaliesData.value.map((item: Metric) => ({
          value: (item.value || 0) * 100,
          anomalyDegree: item.anomaly_degree,
          itemStyle: {
            color:
              item.anomaly_degree === null || item.anomaly_degree === 0
                ? '#909090'
                : item.anomaly_degree > 0
                  ? ANOMALY_COLORS.HIGH
                  : ANOMALY_COLORS.LOW,
          },
        })),
        showSymbol: false,
      },
      {
        name: 'Uncertainty interval lower bound',
        type: 'line',
        data: anomaliesData.value.map((item) => (item.lower_value || 0) * 100),
        lineStyle: {
          opacity: 0,
        },
        stack: 'confidence-band',
        symbol: 'none',
      },
      {
        name: 'Uncertainty interval area',
        type: 'line',
        data: anomaliesData.value.map(
          (item) => (item.upper_value || 0) * 100 - (item.lower_value || 0) * 100,
        ),
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
        data: anomaliesData.value.map((item) => (item.predicted_value || 0) * 100),
        itemStyle: {
          color: 'rgba(237, 178, 12, 0.5)',
        },
        showSymbol: false,
      },
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
