import client from './client'

/** List patients with optional search and pagination */
export const listPatients = (params = {}) =>
  client.get('/patients/', { params }).then((r) => r.data.data)

/** Get a single patient by id */
export const getPatient = (id) =>
  client.get(`/patients/${id}/`).then((r) => r.data.data)

/** Create a new patient */
export const createPatient = (data) =>
  client.post('/patients/', data).then((r) => r.data.data)

/** Update a patient (partial update supported) */
export const updatePatient = (id, data) =>
  client.put(`/patients/${id}/`, data).then((r) => r.data.data)

/** Delete a patient */
export const deletePatient = (id) => client.delete(`/patients/${id}/`)
