import { useState } from 'react';
import api from '../api/client';

const INITIAL = {
  patientId: '',
  date: '',
  ap_hi: '',
  ap_lo: '',
  cholesterol: '1',
  gluc: '1',
};

export default function AddHealthRecord() {
  const [form, setForm] = useState(INITIAL);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      const res = await api.post(`/patients/${form.patientId}/records/`, {
        date: form.date,
        ap_hi: Number(form.ap_hi),
        ap_lo: Number(form.ap_lo),
        cholesterol: Number(form.cholesterol),
        gluc: Number(form.gluc),
      });
      setMessage(`✅ Record saved! (ID: ${res.data.id}, date: ${res.data.date})`);
      setForm((prev) => ({ ...prev, date: '', ap_hi: '', ap_lo: '', cholesterol: '1', gluc: '1' }));
    } catch (err) {
      setError(err.response?.data ? JSON.stringify(err.response.data) : err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Add Health Record</h2>

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label>Patient ID</label>
          <input
            name="patientId"
            type="number"
            min="1"
            value={form.patientId}
            onChange={handleChange}
            required
            placeholder="Enter patient ID"
          />
        </div>

        <div className="form-group">
          <label>Date</label>
          <input name="date" type="date" value={form.date} onChange={handleChange} required />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Systolic BP (ap_hi)</label>
            <input name="ap_hi" type="number" step="0.1" value={form.ap_hi} onChange={handleChange} required placeholder="e.g. 120" />
          </div>
          <div className="form-group">
            <label>Diastolic BP (ap_lo)</label>
            <input name="ap_lo" type="number" step="0.1" value={form.ap_lo} onChange={handleChange} required placeholder="e.g. 80" />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Cholesterol Level</label>
            <select name="cholesterol" value={form.cholesterol} onChange={handleChange}>
              <option value="1">1 – Normal</option>
              <option value="2">2 – Above Normal</option>
              <option value="3">3 – Well Above Normal</option>
            </select>
          </div>
          <div className="form-group">
            <label>Glucose Level</label>
            <select name="gluc" value={form.gluc} onChange={handleChange}>
              <option value="1">1 – Normal</option>
              <option value="2">2 – Above Normal</option>
              <option value="3">3 – Well Above Normal</option>
            </select>
          </div>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Saving…' : 'Add Record'}
        </button>
      </form>
    </div>
  );
}
