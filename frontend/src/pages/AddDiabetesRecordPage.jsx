import React, { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { createDiabetesRecord } from '../api/diabetes'
import ErrorMessage from '../components/ErrorMessage'

const today = () => new Date().toISOString().split('T')[0]

const INITIAL = {
  date: today(),
  pregnancies: 0,
  glucose: '',
  blood_pressure: '',
  skin_thickness: '',
  insulin: '',
  bmi: '',
  diabetes_pedigree_function: '',
  age: '',
}

export default function AddDiabetesRecordPage() {
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
    if (form.pregnancies < 0 || form.pregnancies > 20) errs.pregnancies = 'Pregnancies must be 0–20.'
    const glucose = Number(form.glucose)
    if (!form.glucose || isNaN(glucose) || glucose < 40 || glucose > 400) errs.glucose = 'Glucose must be 40–400.'
    const bp = Number(form.blood_pressure)
    if (!form.blood_pressure || isNaN(bp) || bp < 40 || bp > 200) errs.blood_pressure = 'Blood pressure must be 40–200.'
    const skin = Number(form.skin_thickness)
    if (form.skin_thickness !== '' && (isNaN(skin) || skin < 0 || skin > 100)) errs.skin_thickness = 'Skin thickness must be 0–100.'
    const insulin = Number(form.insulin)
    if (form.insulin !== '' && (isNaN(insulin) || insulin < 0 || insulin > 1000)) errs.insulin = 'Insulin must be 0–1000.'
    const bmi = Number(form.bmi)
    if (!form.bmi || isNaN(bmi) || bmi < 10 || bmi > 70) errs.bmi = 'BMI must be 10–70.'
    const dpf = Number(form.diabetes_pedigree_function)
    if (!form.diabetes_pedigree_function || isNaN(dpf) || dpf < 0 || dpf > 3) errs.diabetes_pedigree_function = 'DPF must be 0–3.'
    const age = Number(form.age)
    if (!form.age || isNaN(age) || age < 1 || age > 120) errs.age = 'Age must be 1–120.'
    return errs
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length > 0) { setErrors(errs); return }
    setSubmitting(true)
    setApiError(null)
    try {
      await createDiabetesRecord(id, {
        date: form.date,
        pregnancies: Number(form.pregnancies),
        glucose: Number(form.glucose),
        blood_pressure: Number(form.blood_pressure),
        skin_thickness: Number(form.skin_thickness || 0),
        insulin: Number(form.insulin || 0),
        bmi: Number(form.bmi),
        diabetes_pedigree_function: Number(form.diabetes_pedigree_function),
        age: Number(form.age),
      })
      navigate(`/patients/${id}`)
    } catch (err) {
      setApiError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 520 }}>
      <Link to={`/patients/${id}`} style={{ color: '#718096', fontSize: '0.85rem' }}>
        ← Back to Patient
      </Link>
      <h2>Add Diabetes Record</h2>

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
              <label>Pregnancies</label>
              <input type="number" value={form.pregnancies} onChange={set('pregnancies')} min="0" max="20" />
              {errors.pregnancies && <div className="form-error">{errors.pregnancies}</div>}
            </div>
            <div className="form-group">
              <label>Glucose *</label>
              <input type="number" value={form.glucose} onChange={set('glucose')} min="40" max="400" />
              {errors.glucose && <div className="form-error">{errors.glucose}</div>}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div className="form-group">
              <label>Blood Pressure *</label>
              <input type="number" value={form.blood_pressure} onChange={set('blood_pressure')} min="40" max="200" />
              {errors.blood_pressure && <div className="form-error">{errors.blood_pressure}</div>}
            </div>
            <div className="form-group">
              <label>Skin Thickness</label>
              <input type="number" value={form.skin_thickness} onChange={set('skin_thickness')} min="0" max="100" />
              {errors.skin_thickness && <div className="form-error">{errors.skin_thickness}</div>}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div className="form-group">
              <label>Insulin</label>
              <input type="number" value={form.insulin} onChange={set('insulin')} min="0" max="1000" />
              {errors.insulin && <div className="form-error">{errors.insulin}</div>}
            </div>
            <div className="form-group">
              <label>BMI *</label>
              <input type="number" value={form.bmi} onChange={set('bmi')} min="10" max="70" step="0.1" />
              {errors.bmi && <div className="form-error">{errors.bmi}</div>}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div className="form-group">
              <label>Diabetes Pedigree Function *</label>
              <input type="number" value={form.diabetes_pedigree_function} onChange={set('diabetes_pedigree_function')} min="0" max="3" step="0.01" />
              {errors.diabetes_pedigree_function && <div className="form-error">{errors.diabetes_pedigree_function}</div>}
            </div>
            <div className="form-group">
              <label>Age *</label>
              <input type="number" value={form.age} onChange={set('age')} min="1" max="120" />
              {errors.age && <div className="form-error">{errors.age}</div>}
            </div>
          </div>
        </div>

        <div className="flex gap-sm">
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Saving…' : 'Save Diabetes Record'}
          </button>
          <Link to={`/patients/${id}`} className="btn btn-outline">Cancel</Link>
        </div>
      </form>
    </div>
  )
}
