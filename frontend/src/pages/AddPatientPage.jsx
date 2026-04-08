import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { createPatient } from '../api/patients'
import ErrorMessage from '../components/ErrorMessage'

const INITIAL = {
  name: '',
  age: '',
  gender: '1',
  height: '',
  weight: '',
  smoke: false,
  alco: false,
  active: true,
}

export default function AddPatientPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState(INITIAL)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [apiError, setApiError] = useState(null)

  const set = (field) => (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm((f) => ({ ...f, [field]: val }))
    setErrors((er) => ({ ...er, [field]: undefined }))
  }

  const validate = () => {
    const errs = {}
    if (!form.name.trim()) errs.name = 'Name is required.'
    const age = Number(form.age)
    if (!form.age || isNaN(age) || age < 1 || age > 120) errs.age = 'Age must be 1–120.'
    const height = Number(form.height)
    if (!form.height || isNaN(height) || height < 50 || height > 250) errs.height = 'Height must be 50–250 cm.'
    const weight = Number(form.weight)
    if (!form.weight || isNaN(weight) || weight < 10 || weight > 400) errs.weight = 'Weight must be 10–400 kg.'
    return errs
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length > 0) { setErrors(errs); return }
    setSubmitting(true)
    setApiError(null)
    try {
      const patient = await createPatient({
        name: form.name.trim(),
        age: Number(form.age),
        gender: Number(form.gender),
        height: Number(form.height),
        weight: Number(form.weight),
        smoke: form.smoke,
        alco: form.alco,
        active: form.active,
      })
      navigate(`/patients/${patient.id}`)
    } catch (err) {
      setApiError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 520 }}>
      <Link to="/patients" style={{ color: '#718096', fontSize: '0.85rem' }}>← Back to Patients</Link>
      <h2>Add New Patient</h2>

      {apiError && <ErrorMessage message={apiError} />}

      <form onSubmit={handleSubmit} noValidate>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', marginTop: 0 }}>Demographics</h3>

          <div className="form-group">
            <label>Full Name *</label>
            <input type="text" value={form.name} onChange={set('name')} placeholder="e.g. Jane Doe" />
            {errors.name && <div className="form-error">{errors.name}</div>}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div className="form-group">
              <label>Age (years) *</label>
              <input type="number" value={form.age} onChange={set('age')} min="1" max="120" />
              {errors.age && <div className="form-error">{errors.age}</div>}
            </div>
            <div className="form-group">
              <label>Gender *</label>
              <select value={form.gender} onChange={set('gender')}>
                <option value="1">Male</option>
                <option value="2">Female</option>
              </select>
            </div>
            <div className="form-group">
              <label>Height (cm) *</label>
              <input type="number" value={form.height} onChange={set('height')} min="50" max="250" step="0.1" />
              {errors.height && <div className="form-error">{errors.height}</div>}
            </div>
            <div className="form-group">
              <label>Weight (kg) *</label>
              <input type="number" value={form.weight} onChange={set('weight')} min="10" max="400" step="0.1" />
              {errors.weight && <div className="form-error">{errors.weight}</div>}
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem', marginTop: 0 }}>Lifestyle</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {[
              { key: 'smoke', label: '🚬 Smoker' },
              { key: 'alco', label: '🍷 Alcohol consumer' },
              { key: 'active', label: '🏃 Physically active' },
            ].map(({ key, label }) => (
              <label key={key} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={form[key]}
                  onChange={set(key)}
                  style={{ width: 'auto', margin: 0 }}
                />
                {label}
              </label>
            ))}
          </div>
        </div>

        <div className="flex gap-sm">
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Saving…' : 'Create Patient'}
          </button>
          <Link to="/patients" className="btn btn-outline">Cancel</Link>
        </div>
      </form>
    </div>
  )
}
