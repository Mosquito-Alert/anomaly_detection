<template>
  <div class="bg-white q-pa-sm rounded-borders">
    <div class="row">
      <span class="text-h6 text-weight-regular">Autonomous communities</span>
      <q-space />
      <span class="self-end text-weight-thin text-caption">Last {{ numDaysAgo }} days</span>
    </div>
    <q-separator />
    <div>
      <!-- Skeletons -->
      <div v-if="loading">
        <div v-for="index in 15" :key="index" class="row q-pa-xs">
          <q-skeleton type="QBadge" class="q-pr-xs col-1" />
          <q-skeleton class='col-7' />
          <q-space />
          <q-skeleton class="col-2" />
        </div>
      </div>
      <!-- Display grouped data -->
      <div v-for="region in groupedData" :key="region.region_code" class="q-pa-xs">
        <div class="row items-center">
          <q-badge class='col-1 text-center flex justify-center' rounded :color="getBadgeColor(region.usual_percentage)"
            :label="region.usual_percentage + '%'" />
          <span class="col-auto q-pl-xs">{{ region.region_name }}</span>

          <q-space />
          <div class="row beat-bar">
            <div v-for="count_item in region.counts" :key="count_item.date"
              :class="['beat', `bg-anomaly-${count_item.region_status}`]">
              <q-tooltip anchor="top middle" self="bottom middle">
                <div class="col">
                  <span class="text-center text-weight-bold">{{ formatDate(count_item.date) }}</span>
                  <q-separator />
                  <div class="row">{{ count_item.count_is_normal }} Lower</div>
                  <div class="row">{{ count_item.count_anomaly_lower }} Normal</div>
                  <div class="row">{{ count_item.count_anomaly_higher }} Higher</div>
                </div>
              </q-tooltip>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import { ref, watch } from 'vue';
import { date } from 'quasar';

const numDaysAgo = 7

export default {
  props: {
    lastDate: {
      type: Date,
    },
  },
  setup(props) {
    const groupedData = ref([]);

    const loading = ref(!props.lastDate)

    function getBadgeColor(normalPercentage) {
      if (normalPercentage < 60) {
        return 'negative';
      } else if (normalPercentage < 90) {
        return 'warning';
      } else {
        return 'positive';
      }
    }

    function formatDate(inputDate) {
      if (!inputDate) return 'Invalid date';
      return date.formatDate(inputDate, 'YYYY-MM-DD');
    }

    const fetchData = async () => {
      const fromDate = date.subtractFromDate(props.lastDate, { 'days': numDaysAgo })
      const toDate = props.lastDate
      loading.value = true
      try {
        const baseUrl = 'https://mapserver.mosquitoalert.com/geoserver/mosquitoalert/ows'
        const params = new URLSearchParams({
          service: 'WFS',
          version: '2.0.0',
          request: 'GetFeature',
          typeName: 'mosquitoalert:region_summary',
          outputFormat: 'application/json',
          viewparams: `fromDate:${date.formatDate(fromDate, 'YYYY-MM-DD')};toDate:${date.formatDate(toDate, 'YYYY-MM-DD')}`
        });
        const response = await fetch(`${baseUrl}?${params}`);
        const data = await response.json();

        const calculateRegionStatus = (countAnomalyLower, countAnomalyHigher, countNormal) => {
          if (countAnomalyLower === 0 && countAnomalyHigher === 0) {
            return 'usual';
          }
          if (countAnomalyHigher > 0) {
            return 'higher';
          }

          const isMajorityAnomalyLower = countAnomalyLower / (countAnomalyLower + countAnomalyHigher + countNormal) >= 0.5
          if (isMajorityAnomalyLower) {
            return 'lower';
          }

          return 'usual';
        };

        // Group data by region_code and region_name
        const grouped = data.features.reduce((acc, feature) => {
          const { region_code, region_name, date, count_is_normal, count_anomaly_lower, count_anomaly_higher } = feature.properties;

          // Check if region already exists in the accumulator
          let region = acc.find(r => r.region_code === region_code && r.region_name === region_name);

          if (!region) {
            // If region doesn't exist, create a new one
            region = {
              region_code,
              region_name,
              counts: []
            };
            acc.push(region);
          }

          // Add the counts for the specific date
          region.counts.push({
            date,
            count_is_normal,
            count_anomaly_lower,
            count_anomaly_higher,
            region_status: calculateRegionStatus(count_anomaly_lower, count_anomaly_higher, count_is_normal)
          });

          region.counts.sort((a, b) => new Date(a.date) - new Date(b.date));

          return acc;
        }, []);

        // Calculate usual_percentage after the reduce
        grouped.forEach(region => {
          const normalCount = region.counts.filter(c => c.region_status === 'usual').length;
          const totalCount = region.counts.length;
          // Remove decimals if the number is an integer
          const usual_percentage = ((normalCount / totalCount) * 100).toFixed(0)
          const formattedPerc = usual_percentage % 1 === 0 ? usual_percentage.toString().split('.')[0] : usual_percentage;

          region.usual_percentage = formattedPerc;
        });

        // Update the ref with the grouped result
        grouped.sort((a, b) => a.region_name.localeCompare(b.region_name));
        groupedData.value = grouped;
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        loading.value = false
      }
    };

    watch(() => props.lastDate, (newValue, oldValue) => {
      groupedData.value = [];
      if (newValue) {
        fetchData();
      }
    }, { immediate: true })

    return {
      loading,
      groupedData,
      numDaysAgo,
      getBadgeColor,
      formatDate
    };
  }
}

</script>

<style lang="scss" scoped>
.beat-bar {
  transform: translateX(0px);
}

.beat {
  width: 5px;
  height: 16px;
  margin: 2px;
  border-radius: 50rem;
}

.beat:hover {
  transform: scale(1.2);
}
</style>
