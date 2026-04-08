import React from 'react'

const CHOL_LABELS = { 1: 'Normal', 2: 'Above Normal', 3: 'Well Above Normal' }
const GLUC_LABELS = { 1: 'Normal', 2: 'Above Normal', 3: 'Well Above Normal' }

export default function RecordTable({ records, onDelete }) {
  if (!records || records.length === 0) {
    return <p style={{ color: '#718096', fontStyle: 'italic' }}>No health records yet.</p>
  }
  return (
    <div style={{ overflowX: 'auto' }}>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Systolic BP</th>
            <th>Diastolic BP</th>
            <th>Cholesterol</th>
            <th>Glucose</th>
            {onDelete && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r.id}>
              <td>{r.date}</td>
              <td>{r.ap_hi} mmHg</td>
              <td>{r.ap_lo} mmHg</td>
              <td>{CHOL_LABELS[r.cholesterol] ?? r.cholesterol}</td>
              <td>{GLUC_LABELS[r.gluc] ?? r.gluc}</td>
              {onDelete && (
                <td>
                  <button
                    className="btn btn-danger"
                    style={{ padding: '0.2rem 0.5rem', fontSize: '0.78rem' }}
                    onClick={() => onDelete(r.id)}
                  >
                    Delete
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
