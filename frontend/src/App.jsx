import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import PatientListPage from './pages/PatientListPage'
import PatientDetailPage from './pages/PatientDetailPage'
import AddPatientPage from './pages/AddPatientPage'
import AddRecordPage from './pages/AddRecordPage'
import PredictionPage from './pages/PredictionPage'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main style={{ maxWidth: 960, margin: '0 auto', padding: '1.5rem 1rem' }}>
        <Routes>
          <Route path="/" element={<Navigate to="/patients" replace />} />
          <Route path="/patients" element={<PatientListPage />} />
          <Route path="/patients/new" element={<AddPatientPage />} />
          <Route path="/patients/:id" element={<PatientDetailPage />} />
          <Route path="/patients/:id/records/new" element={<AddRecordPage />} />
          <Route path="/patients/:id/predictions" element={<PredictionPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}
