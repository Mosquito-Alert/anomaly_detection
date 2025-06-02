import { Configuration, RegionsApi, MetricsApi } from 'anomaly-detection';

const configuration = new Configuration({
  basePath: '/api',
});

export const metricsApi = new MetricsApi(configuration);
export const regionsApi = new RegionsApi(configuration);
