import React from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const { pathname } = useLocation()
  return (
    <nav style={{
      background: '#2b6cb0',
      color: '#fff',
      padding: '0 1.5rem',
      display: 'flex',
      alignItems: 'center',
      gap: '1.5rem',
      height: 52,
      boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
    }}>
      <Link to="/patients" style={{
        color: '#fff', fontWeight: 700, fontSize: '1.05rem', letterSpacing: 0.3
      }}>
        🏥 AI Clinical Risk
      </Link>
      <Link
        to="/patients"
        style={{ color: pathname.startsWith('/patients') ? '#bee3f8' : '#fff', fontWeight: 500 }}
      >
        Patients
      </Link>
      <Link
        to="/patients/new"
        style={{ color: pathname === '/patients/new' ? '#bee3f8' : '#fff', fontWeight: 500 }}
      >
        + Add Patient
      </Link>
    </nav>
  )
}
