import client from './client'

/** List all health records for a patient */
export const listRecords = (patientId) =>
  client.get(`/patients/${patientId}/records/`).then((r) => r.data.data)

/** Add a health record for a patient */
export const createRecord = (patientId, data) =>
  client.post(`/patients/${patientId}/records/`, data).then((r) => r.data.data)

/** Delete a health record */
export const deleteRecord = (patientId, recordId) =>
  client.delete(`/patients/${patientId}/records/${recordId}/`)
