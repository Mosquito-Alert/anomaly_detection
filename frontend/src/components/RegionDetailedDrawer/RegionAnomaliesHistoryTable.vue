<template>
  <div class="">
    <q-table
      flat
      title="Anomalies history"
      :rows="data"
      :columns="columns"
      :loading="loading"
      v-model:pagination="pagination"
    >
      <template v-slot:loading>
        <q-inner-loading showing color="primary" />
      </template>

      <template v-slot:body-cell-anomaly="props">
        <q-td :props="props">
          <div>
            <q-badge :color="anomalyClassificationStyle(props.value)" :label="props.value" />
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { Metric, PaginatedMetricList } from 'anomaly-detection';
import { useMapStore } from 'src/stores/mapStore';
import { date, QTableProps } from 'quasar';
import { anomalyClassificationStyle, classifyAnomaly } from 'src/utils/anomalyClassification';
import { historyPageSize } from 'src/constants/config';

const mapStore = useMapStore();

const history = computed<PaginatedMetricList>(
  () => mapStore.selectedRegionHistory as PaginatedMetricList,
);
const loading = computed(() => mapStore.fetchingRegionHistory);
const data = computed<Array<Metric>>(() => {
  if (!history.value || !history.value.results) {
    return [];
  }
  return history.value.results;
});
// TODO: Pagination
const pagination = ref({
  rowsPerPage: historyPageSize,
  sortBy: 'date',
  descending: true,
});

const columns: QTableProps['columns'] = [
  {
    name: 'date',
    field: 'date',
    required: true,
    label: 'Date',
    align: 'left',
    sortable: true,
    sortOrder: 'da',
    format: (val: string, row: any): string => date.formatDate(new Date(val), 'YYYY-MM-DD'),
  },
  {
    name: 'anomaly',
    field: 'anomaly_degree',
    required: true,
    align: 'center',
    label: 'Anomaly',
    format: (val: number, row: any): string => classifyAnomaly(val),
  },
  {
    name: 'value',
    field: 'value',
    required: true,
    label: 'Bites Index (%)',
    format: (val: number, row: any): string => (val ? `${(val * 100).toFixed(2)}%` : 'N/A'),
    align: 'center',
  },
  {
    name: 'lowerValue',
    field: 'lower_value',
    required: true,
    label: 'Lower bound (%)',
    format: (val: number, row: any): string => (val ? `${(val * 100).toFixed(2)}%` : 'N/A'),
    align: 'center',
  },
  {
    name: 'upperValue',
    field: 'upper_value',
    required: true,
    label: 'Upper bound (%)',
    format: (val: number, row: any): string => (val ? `${(val * 100).toFixed(2)}%` : 'N/A'),
    align: 'center',
  },
];
</script>
