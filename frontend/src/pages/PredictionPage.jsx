import React, { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { listPredictions, triggerPrediction } from '../api/predictions'
import PredictionResult from '../components/PredictionResult'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function PredictionPage() {
  const { id } = useParams()
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [predicting, setPredicting] = useState(false)
  const [predError, setPredError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listPredictions(id)
      setPredictions(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { load() }, [load])

  const handlePredict = async () => {
    setPredicting(true)
    setPredError(null)
    try {
      const result = await triggerPrediction(id)
      setPredictions([result, ...predictions])
    } catch (err) {
      setPredError(err.message)
    } finally {
      setPredicting(false)
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <Link to={`/patients/${id}`} style={{ color: '#718096', fontSize: '0.85rem' }}>
        ← Back to Patient
      </Link>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '0.5rem 0 1rem' }}>
        <h2 style={{ margin: 0 }}>CVD Risk Predictions</h2>
        <button className="btn btn-primary" onClick={handlePredict} disabled={predicting}>
          {predicting ? 'Running…' : '🔮 Run New Prediction'}
        </button>
      </div>

      {error && <ErrorMessage message={error} onRetry={load} />}
      {predError && <ErrorMessage message={predError} />}
      {predicting && <LoadingSpinner message="Running CVD risk prediction…" />}

      {predictions.length === 0 && !loading && !predicting && (
        <div className="card" style={{ textAlign: 'center', color: '#718096' }}>
          <p>No predictions yet. Click "Run New Prediction" to start.</p>
        </div>
      )}

      {predictions.map((pred, i) => (
        <div key={pred.id}>
          {i === 0 && <h3>Latest Prediction</h3>}
          {i === 1 && <h3 style={{ marginTop: '1.5rem' }}>Previous Predictions</h3>}
          <PredictionResult prediction={pred} />
        </div>
      ))}
    </div>
  )
}
