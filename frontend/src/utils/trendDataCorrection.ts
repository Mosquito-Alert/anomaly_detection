import { MetricTrend } from 'anomaly-detection';

/**
 * Corrects the trend data by associating each value with its corresponding date,
 * given the last date in the trend.
 * @param trendData
 * @return An array of objects containing the value and date for each entry in the trend data.
 */
export const trendDataCorrection = (
  trend: number[],
  lastDate: Date,
): { value: number; date: Date }[] => {
  // Map each trend value with a date given the last date in the trend
  return trend.map((item: number, index: number): { date: Date; value: number } => {
    // Number of days until the trend date given the index of the current trend value
    const daysUntilTrendDate = trend.length - 1 - index;
    // Calculate the date for each trend value
    const date = new Date(lastDate);
    date.setDate(date.getDate() - daysUntilTrendDate);
    return { date, value: Number(item) };
  });
};
