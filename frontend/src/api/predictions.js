import client from './client'

/** Trigger a CVD prediction for a patient */
export const triggerPrediction = (patientId) =>
  client.post(`/patients/${patientId}/predict/`).then((r) => r.data.data)

/** List past predictions for a patient */
export const listPredictions = (patientId) =>
  client.get(`/patients/${patientId}/predictions/`).then((r) => r.data.data)
