<template>
  <q-table :columns="columns" :rows="data" :loading="loading" flat title="Last anomalies"
    v-model:pagination="pagination">
    <template v-slot:loading>
      <q-inner-loading showing color="primary" />
    </template>

    <template v-slot:body-cell-anomalyType="props">
      <q-td :props="props">
        <div>
          <q-badge :color="getColor(props.value)"
            :label="props.value === 0 ? 'Usual' : (props.value === 1 ? 'Higher' : (props.value === -1 ? 'Lower' : 'grey'))" />
        </div>
      </q-td>
    </template>
  </q-table>
</template>

<script setup>

import { date } from 'quasar'
import { ref } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const pagination = ref({
  rowsPerPage: 5,
  sortBy: 'date',
  descending: true,
})

const columns = [
  {
    name: 'date',
    field: 'date',
    required: true,
    label: 'Date',
    align: 'left',
    sortable: true,
    sortOrder: 'da',
    format: (val, row) => date.formatDate(new Date(val), 'YYYY-MM-DD'),
  },
  {
    name: 'anomalyType',
    field: 'anomaly',
    required: true,
    align: 'center',
    label: 'Anomaly Type',
  },
  {
    name: 'y',
    field: 'y',
    required: true,
    label: 'VRI (%)',
    format: (val, row) => `${val.toFixed(2)}%`,
    align: 'center',
  },
  {
    name: 'yhat_lower',
    field: 'yhat_lower',
    required: true,
    label: 'Lower bound (%)',
    format: (val, row) => `${val.toFixed(2)}%`,
    align: 'center',
  },
  {
    name: 'yhat_upper',
    field: 'yhat_upper',
    required: true,
    label: 'Upper bound (%)',
    format: (val, row) => `${val.toFixed(2)}%`,
    align: 'center',
  }
]

function getColor(value) {
  let color;
  switch (value) {
    case 1:
      color = 'anomaly-higher'; // Get from css
      break;
    case -1:
      color = 'anomaly-lower'; // Get from css
      break;
    case 0:
      color = 'anomaly-usual'; // Get from css
      break;
    default:
      color = '#808080';
  }

  return color
}

</script>
