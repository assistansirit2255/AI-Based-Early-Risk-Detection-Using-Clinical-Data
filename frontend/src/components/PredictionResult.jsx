import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

function ShapChart({ shapValues }) {
  if (!shapValues) return null

  const data = Object.entries(shapValues)
    .map(([feature, value]) => ({ feature, value: Number(value.toFixed(4)) }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 10)

  return (
    <div style={{ marginTop: '1rem' }}>
      <h4 style={{ marginBottom: '0.5rem' }}>🔍 Feature Attributions (SHAP)</h4>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} layout="vertical" margin={{ left: 60 }}>
          <XAxis type="number" tickFormatter={(v) => v.toFixed(3)} fontSize={11} />
          <YAxis type="category" dataKey="feature" width={80} fontSize={11} />
          <Tooltip formatter={(v) => v.toFixed(4)} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.value >= 0 ? '#fc8181' : '#68d391'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p style={{ fontSize: '0.78rem', color: '#718096', marginTop: '0.4rem' }}>
        Red = increases risk · Green = decreases risk
      </p>
    </div>
  )
}

export default function PredictionResult({ prediction }) {
  if (!prediction) return null

  const isHigh = prediction.prediction === 1
  const pct = (prediction.probability * 100).toFixed(1)

  return (
    <div className="card">
      {/* Risk verdict */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
        <div style={{
          width: 72, height: 72, borderRadius: '50%',
          background: isHigh ? '#fed7d7' : '#c6f6d5',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '2rem',
        }}>
          {isHigh ? '🔴' : '🟢'}
        </div>
        <div>
          <div style={{ fontSize: '1.35rem', fontWeight: 700, color: isHigh ? '#c53030' : '#276749' }}>
            {isHigh ? 'High Risk' : 'Low Risk'}
          </div>
          <div style={{ fontSize: '1rem', color: '#4a5568' }}>
            Risk probability: <strong>{pct}%</strong>
          </div>
        </div>
      </div>

      {/* Probability bar */}
      <div style={{ marginBottom: '1rem' }}>
        <div style={{ height: 14, background: '#e2e8f0', borderRadius: 7, overflow: 'hidden' }}>
          <div style={{
            width: `${pct}%`,
            height: '100%',
            background: isHigh ? '#e53e3e' : '#38a169',
            borderRadius: 7,
            transition: 'width 0.6s ease',
          }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#718096', marginTop: 3 }}>
          <span>0%</span><span>50%</span><span>100%</span>
        </div>
      </div>

      {/* Meta info */}
      <div style={{ fontSize: '0.85rem', color: '#718096', display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
        <span>
          Data used: <span className={`badge ${prediction.data_type_used === 'hybrid' ? 'badge-blue' : 'badge-green'}`}>
            {prediction.data_type_used}
          </span>
        </span>
        <span>Records used: {prediction.records_used}</span>
        <span>Records provided: {prediction.records_provided}</span>
        <span>Date: {new Date(prediction.created_at).toLocaleString()}</span>
      </div>

      {/* SHAP warning */}
      {prediction.shap_warning && (
        <div style={{
          marginTop: '0.75rem', padding: '0.5rem 0.75rem',
          background: '#fef3c7', borderRadius: 6, fontSize: '0.82rem', color: '#92400e',
        }}>
          ⚠ SHAP: {prediction.shap_warning}
        </div>
      )}

      {/* SHAP chart */}
      {prediction.shap_values ? (
        <ShapChart shapValues={prediction.shap_values} />
      ) : (
        !prediction.shap_warning && (
          <p style={{ color: '#718096', fontSize: '0.85rem', marginTop: '0.5rem' }}>
            SHAP feature attributions not available.
          </p>
        )
      )}
    </div>
  )
}
