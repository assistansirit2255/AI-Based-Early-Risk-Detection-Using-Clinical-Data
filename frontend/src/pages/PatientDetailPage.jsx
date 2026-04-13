import React, { useState, useEffect, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getPatient, deletePatient } from '../api/patients'
import { listRecords, deleteRecord } from '../api/records'
import { listDiabetesRecords, deleteDiabetesRecord, triggerDiabetesPrediction, listDiabetesPredictions } from '../api/diabetes'
import { triggerPrediction, listPredictions } from '../api/predictions'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import RecordTable from '../components/RecordTable'
import PredictionResult from '../components/PredictionResult'
import DiabetesRecordTable from '../components/DiabetesRecordTable'
import DiabetesPredictionResult from '../components/DiabetesPredictionResult'

export default function PatientDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [patient, setPatient] = useState(null)
  const [records, setRecords] = useState([])
  const [predictions, setPredictions] = useState([])
  const [diabetesRecords, setDiabetesRecords] = useState([])
  const [diabetesPredictions, setDiabetesPredictions] = useState([])
  const [loadingData, setLoadingData] = useState(true)
  const [error, setError] = useState(null)
  const [predicting, setPredicting] = useState(false)
  const [predError, setPredError] = useState(null)
  const [diabetesPredicting, setDiabetesPredicting] = useState(false)
  const [diabetesPredError, setDiabetesPredError] = useState(null)

  const load = useCallback(async () => {
    setLoadingData(true)
    setError(null)
    try {
      const [p, r, preds, dRecords, dPreds] = await Promise.all([
        getPatient(id),
        listRecords(id),
        listPredictions(id),
        listDiabetesRecords(id),
        listDiabetesPredictions(id),
      ])
      setPatient(p)
      setRecords(r)
      setPredictions(preds)
      setDiabetesRecords(dRecords)
      setDiabetesPredictions(dPreds)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingData(false)
    }
  }, [id])

  useEffect(() => { load() }, [load])

  const handleDeletePatient = async () => {
    if (!window.confirm('Delete patient and ALL their records?')) return
    try {
      await deletePatient(id)
      navigate('/patients')
    } catch (err) {
      alert('Failed to delete: ' + err.message)
    }
  }

  const handleDeleteRecord = async (rid) => {
    if (!window.confirm('Delete this record?')) return
    try {
      await deleteRecord(id, rid)
      const updated = await listRecords(id)
      setRecords(updated)
    } catch (err) {
      alert('Failed to delete record: ' + err.message)
    }
  }

  const handleDeleteDiabetesRecord = async (rid) => {
    if (!window.confirm('Delete this diabetes record?')) return
    try {
      await deleteDiabetesRecord(id, rid)
      const updated = await listDiabetesRecords(id)
      setDiabetesRecords(updated)
    } catch (err) {
      alert('Failed to delete diabetes record: ' + err.message)
    }
  }

  const handlePredict = async () => {
    setPredicting(true)
    setPredError(null)
    try {
      const result = await triggerPrediction(id)
      setPredictions((prev) => [result, ...prev])
    } catch (err) {
      setPredError(err.message)
    } finally {
      setPredicting(false)
    }
  }

  const handleDiabetesPredict = async () => {
    setDiabetesPredicting(true)
    setDiabetesPredError(null)
    try {
      const result = await triggerDiabetesPrediction(id)
      setDiabetesPredictions((prev) => [result, ...prev])
    } catch (err) {
      setDiabetesPredError(err.message)
    } finally {
      setDiabetesPredicting(false)
    }
  }

  if (loadingData) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} onRetry={load} />
  if (!patient) return null

  const genderLabel = patient.gender === 1 ? 'Male' : 'Female'
  const bmi = patient.height > 0
    ? (patient.weight / ((patient.height / 100) ** 2)).toFixed(1)
    : '–'

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <div>
          <Link to="/patients" style={{ color: '#718096', fontSize: '0.85rem' }}>← Back to Patients</Link>
          <h2 style={{ margin: '0.3rem 0 0' }}>{patient.name}</h2>
        </div>
        <div className="flex gap-sm">
          <Link to={`/patients/${id}/records/new`} className="btn btn-primary">+ Add Record</Link>
          <Link to={`/patients/${id}/diabetes-records/new`} className="btn btn-outline">+ Add Diabetes Record</Link>
          <button className="btn btn-danger" onClick={handleDeletePatient}>Delete Patient</button>
        </div>
      </div>

      {/* Patient info */}
      <div className="card">
        <h3 style={{ marginBottom: '0.75rem' }}>Patient Profile</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '0.5rem 1.5rem', fontSize: '0.9rem' }}>
          <div><strong>Age:</strong> {patient.age} years</div>
          <div><strong>Gender:</strong> {genderLabel}</div>
          <div><strong>Height:</strong> {patient.height} cm</div>
          <div><strong>Weight:</strong> {patient.weight} kg</div>
          <div><strong>BMI:</strong> {bmi}</div>
          <div><strong>Smoker:</strong> {patient.smoke ? 'Yes' : 'No'}</div>
          <div><strong>Alcohol:</strong> {patient.alco ? 'Yes' : 'No'}</div>
          <div><strong>Active:</strong> {patient.active ? 'Yes' : 'No'}</div>
        </div>
      </div>

      {/* Health Records */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <h3 style={{ margin: 0 }}>Health Records ({records.length})</h3>
          <Link to={`/patients/${id}/records/new`} className="btn btn-outline" style={{ padding: '0.3rem 0.7rem', fontSize: '0.82rem' }}>
            + Add
          </Link>
        </div>
        <RecordTable records={records} onDelete={handleDeleteRecord} />
      </div>

      {/* Prediction Section */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <h3 style={{ margin: 0 }}>CVD Risk Prediction</h3>
          <button
            className="btn btn-primary"
            onClick={handlePredict}
            disabled={predicting || records.length === 0}
          >
            {predicting ? 'Running…' : '🔮 Run Prediction'}
          </button>
        </div>

        {records.length === 0 && (
          <p style={{ color: '#718096', fontStyle: 'italic' }}>
            Add at least one health record to run a prediction.
          </p>
        )}

        {predError && <ErrorMessage message={predError} />}

        {predicting && <LoadingSpinner message="Running CVD risk prediction…" />}

        {predictions.length > 0 && (
          <div>
            <h4 style={{ marginBottom: '0.5rem' }}>Latest Prediction</h4>
            <PredictionResult prediction={predictions[0]} />

            {predictions.length > 1 && (
              <div style={{ marginTop: '1rem' }}>
                <h4>Previous Predictions</h4>
                {predictions.slice(1).map((pred) => (
                  <div key={pred.id} style={{
                    padding: '0.6rem 0.9rem', borderRadius: 6, marginBottom: '0.4rem',
                    background: pred.prediction === 1 ? '#fff5f5' : '#f0fff4',
                    border: `1.5px solid ${pred.prediction === 1 ? '#fc8181' : '#68d391'}`,
                    display: 'flex', gap: '1rem', fontSize: '0.88rem',
                  }}>
                    <span>{pred.prediction === 1 ? '🔴 High Risk' : '🟢 Low Risk'}</span>
                    <span>{(pred.probability * 100).toFixed(1)}%</span>
                    <span className={`badge ${pred.data_type_used === 'hybrid' ? 'badge-blue' : 'badge-green'}`}>
                      {pred.data_type_used}
                    </span>
                    <span style={{ color: '#718096' }}>{new Date(pred.created_at).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {predictions.length === 0 && !predicting && !predError && records.length > 0 && (
          <p style={{ color: '#718096', fontStyle: 'italic' }}>
            No predictions yet. Click "Run Prediction" to analyse this patient.
          </p>
        )}
      </div>

      {/* Diabetes Records */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <h3 style={{ margin: 0 }}>Diabetes Records ({diabetesRecords.length})</h3>
          <Link to={`/patients/${id}/diabetes-records/new`} className="btn btn-outline" style={{ padding: '0.3rem 0.7rem', fontSize: '0.82rem' }}>
            + Add
          </Link>
        </div>
        <DiabetesRecordTable records={diabetesRecords} onDelete={handleDeleteDiabetesRecord} />
      </div>

      {/* Diabetes Prediction Section */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <h3 style={{ margin: 0 }}>Diabetes Risk Prediction</h3>
          <button
            className="btn btn-primary"
            onClick={handleDiabetesPredict}
            disabled={diabetesPredicting || diabetesRecords.length === 0}
          >
            {diabetesPredicting ? 'Running…' : '🧪 Run Prediction'}
          </button>
        </div>

        {diabetesRecords.length === 0 && (
          <p style={{ color: '#718096', fontStyle: 'italic' }}>
            Add at least one diabetes record to run a prediction.
          </p>
        )}

        {diabetesPredError && <ErrorMessage message={diabetesPredError} />}

        {diabetesPredicting && <LoadingSpinner message="Running diabetes risk prediction…" />}

        {diabetesPredictions.length > 0 && (
          <div>
            <h4 style={{ marginBottom: '0.5rem' }}>Latest Prediction</h4>
            <DiabetesPredictionResult prediction={diabetesPredictions[0]} />

            {diabetesPredictions.length > 1 && (
              <div style={{ marginTop: '1rem' }}>
                <h4>Previous Predictions</h4>
                {diabetesPredictions.slice(1).map((pred) => (
                  <div key={pred.id} style={{
                    padding: '0.6rem 0.9rem', borderRadius: 6, marginBottom: '0.4rem',
                    background: pred.prediction === 1 ? '#fff5f5' : '#f0fff4',
                    border: `1.5px solid ${pred.prediction === 1 ? '#fc8181' : '#68d391'}`,
                    display: 'flex', gap: '1rem', fontSize: '0.88rem',
                  }}>
                    <span>{pred.prediction === 1 ? '🔴 High Risk' : '🟢 Low Risk'}</span>
                    <span>{(pred.probability * 100).toFixed(1)}%</span>
                    <span style={{ color: '#718096' }}>{new Date(pred.created_at).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {diabetesPredictions.length === 0 && !diabetesPredicting && !diabetesPredError && diabetesRecords.length > 0 && (
          <p style={{ color: '#718096', fontStyle: 'italic' }}>
            No diabetes predictions yet. Click "Run Prediction" to analyse this patient.
          </p>
        )}
      </div>
    </div>
  )
}
