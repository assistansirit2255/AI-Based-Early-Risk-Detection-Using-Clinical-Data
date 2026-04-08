import { useState } from 'react';
import api from '../api/client';

const INITIAL = {
  name: '',
  age: '',
  gender: '1',
  height: '',
  weight: '',
  smoke: '0',
  alco: '0',
  active: '1',
};

export default function AddPatient() {
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
      const res = await api.post('/patients/', {
        ...form,
        age: Number(form.age),
        gender: Number(form.gender),
        height: Number(form.height),
        weight: Number(form.weight),
        smoke: Number(form.smoke),
        alco: Number(form.alco),
        active: Number(form.active),
      });
      setMessage(`✅ Patient created! ID: ${res.data.id} — ${res.data.name}`);
      setForm(INITIAL);
    } catch (err) {
      setError(err.response?.data ? JSON.stringify(err.response.data) : err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Add Patient</h2>

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label>Full Name</label>
          <input name="name" value={form.name} onChange={handleChange} required placeholder="e.g. Jane Doe" />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Age</label>
            <input name="age" type="number" min="1" max="120" value={form.age} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Gender</label>
            <select name="gender" value={form.gender} onChange={handleChange}>
              <option value="1">Male</option>
              <option value="0">Female</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Height (cm)</label>
            <input name="height" type="number" step="0.1" value={form.height} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Weight (kg)</label>
            <input name="weight" type="number" step="0.1" value={form.weight} onChange={handleChange} required />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Smoker</label>
            <select name="smoke" value={form.smoke} onChange={handleChange}>
              <option value="0">No</option>
              <option value="1">Yes</option>
            </select>
          </div>
          <div className="form-group">
            <label>Alcohol</label>
            <select name="alco" value={form.alco} onChange={handleChange}>
              <option value="0">No</option>
              <option value="1">Yes</option>
            </select>
          </div>
          <div className="form-group">
            <label>Physically Active</label>
            <select name="active" value={form.active} onChange={handleChange}>
              <option value="1">Yes</option>
              <option value="0">No</option>
            </select>
          </div>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Saving…' : 'Add Patient'}
        </button>
      </form>
    </div>
  );
}
