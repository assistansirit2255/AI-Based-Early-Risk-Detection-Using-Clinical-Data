import React, { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { createRecord } from '../api/records'
import ErrorMessage from '../components/ErrorMessage'

const today = () => new Date().toISOString().split('T')[0]

const INITIAL = {
  date: today(),
  ap_hi: '',
  ap_lo: '',
  cholesterol: '1',
  gluc: '1',
}

export default function AddRecordPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState(INITIAL)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [apiError, setApiError] = useState(null)

  const set = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }))

  const validate = () => {
    const errs = {}
    if (!form.date) errs.date = 'Date is required.'
    const hi = Number(form.ap_hi)
    const lo = Number(form.ap_lo)
    if (!form.ap_hi || isNaN(hi) || hi < 60 || hi > 300) errs.ap_hi = 'Systolic BP must be 60–300 mmHg.'
    if (!form.ap_lo || isNaN(lo) || lo < 40 || lo > 200) errs.ap_lo = 'Diastolic BP must be 40–200 mmHg.'
    if (!errs.ap_hi && !errs.ap_lo && lo >= hi) errs.ap_lo = 'Diastolic must be less than systolic BP.'
    return errs
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length > 0) { setErrors(errs); return }
    setSubmitting(true)
    setApiError(null)
    try {
      await createRecord(id, {
        date: form.date,
        ap_hi: Number(form.ap_hi),
        ap_lo: Number(form.ap_lo),
        cholesterol: Number(form.cholesterol),
        gluc: Number(form.gluc),
      })
      navigate(`/patients/${id}`)
    } catch (err) {
      setApiError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 480 }}>
      <Link to={`/patients/${id}`} style={{ color: '#718096', fontSize: '0.85rem' }}>
        ← Back to Patient
      </Link>
      <h2>Add Health Record</h2>

      {apiError && <ErrorMessage message={apiError} />}

      <form onSubmit={handleSubmit} noValidate>
        <div className="card">
          <div className="form-group">
            <label>Date *</label>
            <input type="date" value={form.date} onChange={set('date')} max={today()} />
            {errors.date && <div className="form-error">{errors.date}</div>}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div className="form-group">
              <label>Systolic BP (ap_hi) *</label>
              <input type="number" value={form.ap_hi} onChange={set('ap_hi')} min="60" max="300" placeholder="e.g. 120" />
              {errors.ap_hi && <div className="form-error">{errors.ap_hi}</div>}
            </div>
            <div className="form-group">
              <label>Diastolic BP (ap_lo) *</label>
              <input type="number" value={form.ap_lo} onChange={set('ap_lo')} min="40" max="200" placeholder="e.g. 80" />
              {errors.ap_lo && <div className="form-error">{errors.ap_lo}</div>}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div className="form-group">
              <label>Cholesterol Level</label>
              <select value={form.cholesterol} onChange={set('cholesterol')}>
                <option value="1">1 – Normal</option>
                <option value="2">2 – Above Normal</option>
                <option value="3">3 – Well Above Normal</option>
              </select>
            </div>
            <div className="form-group">
              <label>Glucose Level</label>
              <select value={form.gluc} onChange={set('gluc')}>
                <option value="1">1 – Normal</option>
                <option value="2">2 – Above Normal</option>
                <option value="3">3 – Well Above Normal</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex gap-sm">
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Saving…' : 'Save Record'}
          </button>
          <Link to={`/patients/${id}`} className="btn btn-outline">Cancel</Link>
        </div>
      </form>
    </div>
  )
}
