import client from './client'

/** List all diabetes records for a patient */
export const listDiabetesRecords = (patientId) =>
  client.get(`/patients/${patientId}/diabetes-records/`).then((r) => r.data.data)

/** Add a diabetes record for a patient */
export const createDiabetesRecord = (patientId, data) =>
  client.post(`/patients/${patientId}/diabetes-records/`, data).then((r) => r.data.data)

/** Delete a diabetes record */
export const deleteDiabetesRecord = (patientId, recordId) =>
  client.delete(`/patients/${patientId}/diabetes-records/${recordId}/`)

/** Trigger a diabetes prediction for a patient */
export const triggerDiabetesPrediction = (patientId) =>
  client.post(`/patients/${patientId}/diabetes/predict/`).then((r) => r.data.data)

/** List past diabetes predictions for a patient */
export const listDiabetesPredictions = (patientId) =>
  client.get(`/patients/${patientId}/diabetes-predictions/`).then((r) => r.data.data)
