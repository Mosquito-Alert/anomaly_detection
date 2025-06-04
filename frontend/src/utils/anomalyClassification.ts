export enum AnomalyClassificationEnum {
  High = 'High',
  Low = 'Low',
  Usual = 'Usual',
  N_A = 'N/A',
}

export const classifyAnomaly = (anomalyDegree: number): AnomalyClassificationEnum => {
  // Classify the anomaly degree into one of the categories
  if (anomalyDegree > 0) {
    return AnomalyClassificationEnum.High;
  } else if (anomalyDegree < 0) {
    return AnomalyClassificationEnum.Low;
  } else if (anomalyDegree === 0) {
    return AnomalyClassificationEnum.Usual;
  } else {
    return AnomalyClassificationEnum.N_A;
  }
};

export const anomalyClassificationStyle = (anomalyType: AnomalyClassificationEnum) => {
  let color;
  switch (anomalyType || '') {
    case AnomalyClassificationEnum.Usual:
      color = 'anomaly-usual'; // From app.scss
      break;
    case AnomalyClassificationEnum.Low:
      color = 'anomaly-lower'; // From app.scss
      break;
    case AnomalyClassificationEnum.High:
      color = 'anomaly-higher'; // From app.scss
      break;
    default:
      color = 'grey'; // Default color if no match
  }
  return color;
};
