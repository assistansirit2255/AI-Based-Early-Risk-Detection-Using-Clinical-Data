import React from 'react'
import { Link } from 'react-router-dom'

export default function PatientCard({ patient, onDelete }) {
  const genderLabel = patient.gender === 1 ? 'Male' : 'Female'
  const bmi = patient.height > 0
    ? (patient.weight / ((patient.height / 100) ** 2)).toFixed(1)
    : '–'

  return (
    <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div>
        <Link to={`/patients/${patient.id}`} style={{ fontSize: '1.05rem', fontWeight: 700 }}>
          {patient.name}
        </Link>
        <div style={{ color: '#718096', fontSize: '0.85rem', marginTop: 4 }}>
          Age: {patient.age} · {genderLabel} · BMI: {bmi}
          {patient.smoke && ' · 🚬 Smoker'}
          {patient.alco && ' · 🍷 Alcohol'}
          {patient.active ? ' · 🏃 Active' : ' · 🛋 Inactive'}
        </div>
      </div>
      <div className="flex gap-sm" style={{ flexShrink: 0 }}>
        <Link to={`/patients/${patient.id}`} className="btn btn-outline" style={{ padding: '0.3rem 0.7rem', fontSize: '0.82rem' }}>
          View
        </Link>
        {onDelete && (
          <button
            className="btn btn-danger"
            style={{ padding: '0.3rem 0.7rem', fontSize: '0.82rem' }}
            onClick={() => onDelete(patient.id)}
          >
            Delete
          </button>
        )}
      </div>
    </div>
  )
}
