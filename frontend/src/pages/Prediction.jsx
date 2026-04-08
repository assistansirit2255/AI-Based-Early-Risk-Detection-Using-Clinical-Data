import { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import api from '../api/client';

export default function Prediction() {
  const [patientId, setPatientId] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runPrediction = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.post(`/patients/${patientId}/predict/`);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  const riskLabel = result
    ? result.prediction === 1
      ? '⚠️ High Risk'
      : '✅ Low Risk'
    : null;

  const riskColor = result ? (result.prediction === 1 ? '#e63946' : '#2a9d8f') : '#333';

  const shapData =
    result?.shap_values?.top_features?.map((f) => ({
      feature: f.feature,
      shap: parseFloat(f.shap.toFixed(4)),
      value: f.value,
    })) || [];

  return (
    <div className="card">
      <h2>Disease Risk Prediction</h2>

      <form onSubmit={runPrediction} className="form inline-form">
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
          {loading ? 'Predicting…' : 'Run Prediction'}
        </button>
      </form>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div className="prediction-result">
          {/* Risk label */}
          <div className="risk-card" style={{ borderColor: riskColor }}>
            <div className="risk-label" style={{ color: riskColor }}>
              {riskLabel}
            </div>
            <div className="risk-prob">
              Probability of CVD risk:{' '}
              <strong>{(result.probability * 100).toFixed(1)}%</strong>
            </div>
          </div>

          {/* Probability bar */}
          <div className="prob-bar-bg">
            <div
              className="prob-bar-fill"
              style={{
                width: `${(result.probability * 100).toFixed(1)}%`,
                background: riskColor,
              }}
            />
          </div>
          <p className="prob-bar-label">{(result.probability * 100).toFixed(1)}% risk</p>

          {/* SHAP explanation */}
          {shapData.length > 0 && (
            <div className="shap-section">
              <h3>Top Contributing Features (SHAP)</h3>
              {result.shap_values.base_value !== null && (
                <p className="shap-base">
                  Baseline probability: <strong>{(result.shap_values.base_value * 100).toFixed(1)}%</strong>
                </p>
              )}
              <ResponsiveContainer width="100%" height={260}>
                <BarChart
                  layout="vertical"
                  data={shapData}
                  margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="feature" width={80} />
                  <Tooltip
                    formatter={(val, name, props) => [
                      `SHAP: ${val}  (value: ${props.payload.value})`,
                      props.payload.feature,
                    ]}
                  />
                  <Bar dataKey="shap" name="SHAP value">
                    {shapData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.shap >= 0 ? '#e63946' : '#457b9d'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>

              <table className="data-table shap-table">
                <thead>
                  <tr>
                    <th>Feature</th>
                    <th>Patient Value</th>
                    <th>SHAP Contribution</th>
                  </tr>
                </thead>
                <tbody>
                  {shapData.map((f) => (
                    <tr key={f.feature}>
                      <td>{f.feature}</td>
                      <td>{f.value}</td>
                      <td style={{ color: f.shap >= 0 ? '#e63946' : '#457b9d', fontWeight: 600 }}>
                        {f.shap > 0 ? '+' : ''}{f.shap}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
