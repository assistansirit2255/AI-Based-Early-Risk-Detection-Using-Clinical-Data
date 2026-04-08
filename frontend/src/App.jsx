import { Routes, Route, NavLink } from 'react-router-dom';
import AddPatient from './pages/AddPatient';
import AddHealthRecord from './pages/AddHealthRecord';
import PatientHistory from './pages/PatientHistory';
import Prediction from './pages/Prediction';
import './App.css';

export default function App() {
  return (
    <div className="app">
      <nav className="navbar">
        <span className="navbar-brand">🧠 AI Risk Detection</span>
        <div className="nav-links">
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>
            Add Patient
          </NavLink>
          <NavLink to="/records" className={({ isActive }) => (isActive ? 'active' : '')}>
            Add Record
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => (isActive ? 'active' : '')}>
            Patient History
          </NavLink>
          <NavLink to="/predict" className={({ isActive }) => (isActive ? 'active' : '')}>
            Predict
          </NavLink>
        </div>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<AddPatient />} />
          <Route path="/records" element={<AddHealthRecord />} />
          <Route path="/history" element={<PatientHistory />} />
          <Route path="/predict" element={<Prediction />} />
        </Routes>
      </main>
    </div>
  );
}
