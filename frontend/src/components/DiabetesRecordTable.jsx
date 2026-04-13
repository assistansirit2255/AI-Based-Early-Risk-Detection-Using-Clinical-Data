import React from 'react'

export default function DiabetesRecordTable({ records, onDelete }) {
  if (!records || records.length === 0) {
    return <p style={{ color: '#718096', fontStyle: 'italic' }}>No diabetes records yet.</p>
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Pregnancies</th>
            <th>Glucose</th>
            <th>BP</th>
            <th>Skin</th>
            <th>Insulin</th>
            <th>BMI</th>
            <th>DPF</th>
            <th>Age</th>
            {onDelete && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r.id}>
              <td>{r.date}</td>
              <td>{r.pregnancies}</td>
              <td>{r.glucose}</td>
              <td>{r.blood_pressure}</td>
              <td>{r.skin_thickness}</td>
              <td>{r.insulin}</td>
              <td>{r.bmi}</td>
              <td>{r.diabetes_pedigree_function}</td>
              <td>{r.age}</td>
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
