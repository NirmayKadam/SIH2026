import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ToastProvider from './components/ToastProvider';
import CommandCenterLayout from './layouts/CommandCenterLayout';
import DashboardPage from './pages/DashboardPage';
import GraphExplorerPage from './pages/GraphExplorerPage';
import IngestionPage from './pages/IngestionPage';
import ThreatsPage from './pages/ThreatsPage';
import LoginPage from './pages/LoginPage';
import GeoMapPage from './pages/GeoMapPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

export default function App() {
  const [theme, setTheme] = useState('dark');

  // Apply theme to body
  useEffect(() => {
    if (theme === 'light') {
      document.body.classList.add('theme-light');
    } else {
      document.body.classList.remove('theme-light');
    }
  }, [theme]);

  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<CommandCenterLayout theme={theme} setTheme={setTheme} />}>
                <Route index element={<DashboardPage />} />
                <Route path="graph" element={<GraphExplorerPage />} />
                <Route path="geo" element={<GeoMapPage />} />
                <Route path="ingest" element={<IngestionPage />} />
                <Route path="threats" element={<ThreatsPage />} />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}
