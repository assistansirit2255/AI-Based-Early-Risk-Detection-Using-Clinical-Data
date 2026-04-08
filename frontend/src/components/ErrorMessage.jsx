import React from 'react'

export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-box">
      <strong>⚠ Error:</strong> {message}
      {onRetry && (
        <button
          className="btn btn-outline"
          style={{ marginLeft: '1rem' }}
          onClick={onRetry}
        >
          Retry
        </button>
      )}
    </div>
  )
}
