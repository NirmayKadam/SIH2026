import React, { useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';

const navItems = [
  { path: '/', icon: '📊', label: 'Dashboard' },
  { path: '/graph', icon: '🕸️', label: 'Graph Explorer' },
  { path: '/ingest', icon: '📁', label: 'Ingest Source' },
  { path: '/threats', icon: '⚠', label: 'Threats' },
];

export default function CommandCenterLayout({ theme, setTheme }) {
  const [expanded, setExpanded] = useState(false);

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
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
