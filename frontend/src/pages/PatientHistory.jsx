import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import api from '../api/client';

const CHOLESTEROL_LABEL = { 1: 'Normal', 2: 'Above Normal', 3: 'Well Above Normal' };

export default function PatientHistory() {
  const [patientId, setPatientId] = useState('');
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fetched, setFetched] = useState(false);

  const fetchRecords = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setFetched(false);
    try {
      const res = await api.get(`/patients/${patientId}/records/`);
      setRecords(res.data);
      setFetched(true);
    } catch (err) {
      setError(err.response?.data ? JSON.stringify(err.response.data) : err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = records.map((r) => ({
    date: r.date,
    ap_hi: r.ap_hi,
    ap_lo: r.ap_lo,
    cholesterol: r.cholesterol,
  }));

  return (
    <div className="card">
      <h2>Patient History</h2>

      <form onSubmit={fetchRecords} className="form inline-form">
        <div className="form-group">
          <label>Patient ID</label>
          <input
            type="number"
            min="1"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            required
            placeholder="Enter patient ID"
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Loading…' : 'Fetch Records'}
        </button>
      </form>

      {error && <div className="alert alert-error">{error}</div>}

      {fetched && records.length === 0 && (
        <p className="empty-msg">No records found for this patient.</p>
      )}

      {records.length > 0 && (
        <>
          {/* Table */}
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Date</th>
                  <th>Systolic BP</th>
                  <th>Diastolic BP</th>
                  <th>Cholesterol</th>
                  <th>Glucose</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r, i) => (
                  <tr key={r.id}>
                    <td>{i + 1}</td>
                    <td>{r.date}</td>
                    <td>{r.ap_hi}</td>
                    <td>{r.ap_lo}</td>
                    <td>{CHOLESTEROL_LABEL[r.cholesterol] || r.cholesterol}</td>
                    <td>{CHOLESTEROL_LABEL[r.gluc] || r.gluc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* BP Chart */}
          <h3>Blood Pressure Trend</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={['auto', 'auto']} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="ap_hi" stroke="#e63946" name="Systolic (ap_hi)" dot />
              <Line type="monotone" dataKey="ap_lo" stroke="#457b9d" name="Diastolic (ap_lo)" dot />
            </LineChart>
          </ResponsiveContainer>

          {/* Cholesterol Chart */}
          <h3>Cholesterol Level Trend</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 4]} ticks={[1, 2, 3]} tickFormatter={(v) => CHOLESTEROL_LABEL[v] || v} />
              <Tooltip formatter={(val) => CHOLESTEROL_LABEL[val] || val} />
              <Legend />
              <Line type="monotone" dataKey="cholesterol" stroke="#2a9d8f" name="Cholesterol Level" dot />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}
