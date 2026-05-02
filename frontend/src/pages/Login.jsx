import { useState, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { getTechnicians } from "../api/technicians";

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [technicians, setTechnicians] = useState([]);
  const [techkey, setTechkey] = useState('');
  const [showTechPicker, setShowTechPicker] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    getTechnicians()
      .then(res => setTechnicians(res.data))
      .catch(() => setTechnicians([]));
  }, []);

  const continueAs = (role, extra = {}) => {
    login({ username: username || role, role, ...extra });
    navigate('/' + role);
  };

  const handleTechnicianContinue = () => {
    if (!techkey) return;
    continueAs('technician', { techkey: parseInt(techkey) });
  };

  return (
    <div>
      <div className="logo">
        <img src="./public/repair-matrix.png" />
        <h1 className="login-heading">Login</h1>
      </div>
      <div className="login-form">
        <form onSubmit={e => e.preventDefault()}>
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={e => setUsername(e.target.value)}
          />
          <br /><br />
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
        </form>

        <div className="role-cards">
          <button type="button" className="role-card" onClick={() => continueAs('customer')}>
            Continue as Customer
          </button>
          <button type="button" className="role-card" onClick={() => continueAs('manager')}>
            Continue as Manager
          </button>
          <button
            type="button"
            className="role-card"
            onClick={() => setShowTechPicker(true)}
          >
            Continue as Technician
          </button>
        </div>

        {showTechPicker && (
          <div className="tech-picker">
            <label htmlFor="techkey">Pick a technician:</label>
            <select
              id="techkey"
              value={techkey}
              onChange={e => setTechkey(e.target.value)}
            >
              <option value="">-- select --</option>
              {technicians.map(t => (
                <option key={t.t_techkey} value={t.t_techkey}>
                  {t.t_name} (#{t.t_techkey}) — {t.t_specialty}
                </option>
              ))}
            </select>
            <button type="button" onClick={handleTechnicianContinue}>Sign In</button>
          </div>
        )}
      </div>
    </div>
  );
}
