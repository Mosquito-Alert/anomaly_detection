<template>
  <div class="bg-white rounded-borders">
    <v-chart style="height: 250px" :option="option" :loading="loading" />
  </div>
</template>

<script>
import { date, getCssVar } from 'quasar'
import { computed } from "vue"

import { ANOMALY_COLORS } from 'src/constants/colors'

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
    data: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const option = computed(() => {
      return {
        title: {
          text: 'VRI time series',
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
              color: '#222'
            }
          },
          formatter: function (params) {
            return (
              '<strong>' + params[3].name + '</strong>' +
              '<br/><hr>' +
              '<span>Value: ' + params[0].value.toFixed(2) + '%</span><br/>' +
              '<span>Lower bound: ' + params[1].value.toFixed(2) + '%</span><br/>' +
              '<span>Higher bound: ' + params[2].value.toFixed(2) + '%</span><br/>'
            );
          }
        },
        legend: {
          data: ['Actuals', 'Forecast', 'Trend'],
          selected: {
            'Trend': false
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: props.data.map(function (item) {
            return date.formatDate(item.date, 'YYYY-MM-DD');
          }),
          boundaryGap: false
        },
        yAxis: {
          // min: 0, // Sets the minimum value to 0
          axisLabel: {
            formatter: function (val) {
              return val.toFixed(0) + '%'; // Converts fractions to percentages
            }
          },
          axisPointer: {
            label: {
              formatter: function (params) {
                return params.value.toFixed(2) + '%'; // Converts fractions to percentages
              }
            }
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
            symbolSize: function (value, params) {
              return 2
              return params.data.importance * 2
            },
            itemStyle: {
              color: '#909090'
            },
            data: props.data.map(function (item) {
              return {
                value: item.y * 1.0,
                importance: item.importance,
                itemStyle: {
                  color: item.anomaly === 0 ? '#909090' : (item.anomaly === 1 ? ANOMALY_COLORS.HIGH : (item.anomaly === -1 ? ANOMALY_COLORS.LOW : '#909090')),
                }
              };
            }),
            showSymbol: false
          },
          {
            name: 'Uncertainty internval',
            type: 'line',
            data: props.data.map(function (item) {
              return item.yhat_lower;
            }),
            lineStyle: {
              opacity: 0
            },
            stack: 'confidence-band',
            symbol: 'none'
          },
          {
            name: 'Uncertainty internval',
            type: 'line',
            data: props.data.map(function (item) {
              return item.yhat_upper - item.yhat_lower;
            }),
            lineStyle: {
              opacity: 0
            },
            areaStyle: {
              color: 'rgba(237, 178, 12, 0.3)'
            },
            stack: 'confidence-band',
            symbol: 'none'
          },
          {
            name: 'Forecast',
            type: 'line',
            data: props.data.map(function (item) {
              return item.yhat * 1.0;
            }),
            itemStyle: {
              color: 'rgba(237, 178, 12, 0.5)'
            },
            showSymbol: false
          },
          {
            name: 'Trend',
            type: 'line',
            data: props.data.map(function (item) {
              return item.trend * 1.0;
            }),
            itemStyle: {
              color: getCssVar('accent')
            },
            showSymbol: false
          },
        ]
      }
    })

    return {
      option
    }
  }
}

</script>
