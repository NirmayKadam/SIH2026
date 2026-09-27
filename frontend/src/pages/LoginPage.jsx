import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (username && password) {
      login(username, password);
      navigate('/');
    }
  };

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop") center/cover no-repeat',
      position: 'relative'
    }}>
      <div style={{
        position: 'absolute', inset: 0, background: 'rgba(15, 23, 42, 0.8)', zIndex: 0
      }} />
      <div className="glass-panel" style={{
        position: 'relative',
        zIndex: 1,
        width: '400px',
        padding: '40px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🛡️</div>
        <h1 style={{ color: 'var(--text-main)', marginBottom: '8px', letterSpacing: '2px' }}>NCRB SYSTEM</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '32px', textAlign: 'center', fontSize: '14px' }}>
          Restricted Access. Authorized Personnel Only.
        </p>

        <form onSubmit={handleLogin} style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase' }}>Officer ID</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. admin or investigator"
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'rgba(0, 0, 0, 0.2)',
                border: '1px solid var(--panel-border)',
                borderRadius: '6px',
                color: 'var(--text-main)',
                outline: 'none',
              }}
              required
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase' }}>Secure PIN</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'rgba(0, 0, 0, 0.2)',
                border: '1px solid var(--panel-border)',
                borderRadius: '6px',
                color: 'var(--text-main)',
                outline: 'none',
              }}
              required
            />
          </div>
          <button type="submit" style={{
            marginTop: '16px',
            padding: '14px',
            background: 'var(--neon-cyan)',
            color: '#000',
            border: 'none',
            borderRadius: '6px',
            fontWeight: 'bold',
            cursor: 'pointer',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            transition: 'all 0.2s'
          }}>
            Authenticate
          </button>
        </form>
      </div>
    </div>
  );
}
