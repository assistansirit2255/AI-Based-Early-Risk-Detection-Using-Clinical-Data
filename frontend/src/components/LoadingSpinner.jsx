import React from 'react'

export default function LoadingSpinner({ message = 'Loading…' }) {
  return (
    <div className="center" style={{ flexDirection: 'column', padding: '3rem', gap: '1rem' }}>
      <div className="spinner" />
      <p style={{ color: '#718096', margin: 0 }}>{message}</p>
    </div>
  )
}
