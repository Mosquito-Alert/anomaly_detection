import { Configuration, GeoApi, MetricsApi } from 'anomaly-detection';

const configuration = new Configuration({
  basePath: '/api',
});

export const metricsApi = new MetricsApi(configuration);
export const geoApi = new GeoApi(configuration);
