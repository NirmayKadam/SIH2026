import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ToastProvider from './components/ToastProvider';
import CommandCenterLayout from './layouts/CommandCenterLayout';
import DashboardPage from './pages/DashboardPage';
import GraphExplorerPage from './pages/GraphExplorerPage';
import IngestionPage from './pages/IngestionPage';
import ThreatsPage from './pages/ThreatsPage';

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
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<CommandCenterLayout theme={theme} setTheme={setTheme} />}>
            <Route index element={<DashboardPage />} />
            <Route path="graph" element={<GraphExplorerPage />} />
            <Route path="ingest" element={<IngestionPage />} />
            <Route path="threats" element={<ThreatsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  );
}
