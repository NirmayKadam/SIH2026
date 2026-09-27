import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/ToastProvider';

const navItems = [
  { path: '/', icon: '📊', label: 'Dashboard' },
  { path: '/graph', icon: '🕸️', label: 'Graph Explorer' },
  { path: '/geo', icon: '🌍', label: 'Geo Intelligence' },
  { path: '/ingest', icon: '📁', label: 'Ingest Source' },
  { path: '/threats', icon: '⚠', label: 'Threats' },
];

export default function CommandCenterLayout({ theme, setTheme }) {
  const [expanded, setExpanded] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleExport = () => {
    if (user?.role !== 'admin') {
      toast.error('ACCESS DENIED: Your role lacks export privileges to prevent data exfiltration.');
      return;
    }
    toast.success('Export initiated for Admin.');
  };

  return (
    <div className="command-center-layout">
      {/* Sidebar */}
      <nav 
        className={`sidebar ${expanded ? 'expanded' : 'collapsed'}`}
        onMouseEnter={() => setExpanded(true)}
        onMouseLeave={() => setExpanded(false)}
      >
        <div style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '12px', borderBottom: '1px solid var(--panel-border)', height: '64px' }}>
          <span style={{ fontSize: '24px' }}>🛡️</span>
          {expanded && (
            <span style={{ fontWeight: '700', fontSize: '13px', letterSpacing: '0.5px', color: 'var(--text-main)', whiteSpace: 'nowrap' }}>
              NCRB SYSTEM
            </span>
          )}
        </div>
        
        <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '4px', borderBottom: '1px solid var(--panel-border)' }}>
          {expanded ? (
             <>
               <span style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Logged in as</span>
               <span style={{ fontSize: '13px', color: 'var(--neon-cyan)', fontWeight: 'bold' }}>{user?.username} ({user?.role})</span>
             </>
          ) : (
             <span style={{ fontSize: '16px', textAlign: 'center' }}>👤</span>
          )}
        </div>

        <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', gap: '8px', padding: '12px 8px' }}>
          {navItems.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <span className="sidebar-icon">{item.icon}</span>
              {expanded && <span className="sidebar-label">{item.label}</span>}
            </NavLink>
          ))}
          
          <button 
            className="sidebar-link" 
            onClick={handleExport}
            style={{ background: 'transparent', border: 'none', justifyContent: 'flex-start', color: 'var(--neon-amber)', marginTop: 'auto' }}
          >
            <span className="sidebar-icon">💾</span>
            {expanded && <span className="sidebar-label">Export Data</span>}
          </button>
        </div>

        {/* Footer actions */}
        <div style={{ padding: '12px 8px', borderTop: '1px solid var(--panel-border)' }}>
          <button 
            className="sidebar-link" 
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            style={{ width: '100%', background: 'transparent', border: 'none', justifyContent: 'flex-start' }}
          >
            <span className="sidebar-icon">{theme === 'dark' ? '☀️' : '🌙'}</span>
            {expanded && <span className="sidebar-label">{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>}
          </button>
          
          <button 
            className="sidebar-link" 
            onClick={handleLogout}
            style={{ width: '100%', background: 'transparent', border: 'none', justifyContent: 'flex-start', color: '#ef4444' }}
          >
            <span className="sidebar-icon">🚪</span>
            {expanded && <span className="sidebar-label">Logout</span>}
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
