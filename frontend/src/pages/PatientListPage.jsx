import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { listPatients, deletePatient } from '../api/patients'
import PatientCard from '../components/PatientCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function PatientListPage() {
  const [data, setData] = useState({ count: 0, results: [] })
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await listPatients({ search, page })
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [search, page])

  useEffect(() => { load() }, [load])

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this patient and all their records?')) return
    try {
      await deletePatient(id)
      load()
    } catch (err) {
      alert('Failed to delete: ' + err.message)
    }
  }

  const totalPages = Math.ceil(data.count / (data.page_size || 20))

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ margin: 0 }}>Patients ({data.count})</h2>
        <Link to="/patients/new" className="btn btn-primary">+ Add Patient</Link>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Search by name…"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          style={{
            padding: '0.5rem 0.75rem', border: '1.5px solid #cbd5e0',
            borderRadius: 6, fontSize: '0.95rem', width: '100%', maxWidth: 380,
          }}
        />
      </div>

      {loading && <LoadingSpinner />}
      {!loading && error && <ErrorMessage message={error} onRetry={load} />}

      {!loading && !error && data.results.length === 0 && (
        <div className="card" style={{ textAlign: 'center', color: '#718096' }}>
          <p>No patients found. <Link to="/patients/new">Add the first one.</Link></p>
        </div>
      )}

      {!loading && !error && data.results.map((p) => (
        <PatientCard key={p.id} patient={p} onDelete={handleDelete} />
      ))}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex gap-sm" style={{ marginTop: '1rem', justifyContent: 'center' }}>
          <button className="btn btn-outline" onClick={() => setPage(p => p - 1)} disabled={page <= 1}>
            ← Prev
          </button>
          <span style={{ lineHeight: '2.1rem', color: '#4a5568' }}>
            Page {page} of {totalPages}
          </span>
          <button className="btn btn-outline" onClick={() => setPage(p => p + 1)} disabled={page >= totalPages}>
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
