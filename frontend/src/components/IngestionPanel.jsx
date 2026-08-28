import React, { useState } from 'react';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function IngestionPanel() {
  const [sourceType, setSourceType] = useState('icij_offshore_leaks');
  const [sourcePath, setSourcePath] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  const handleIngest = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch(`${BASE_URL}/api/ingestion/documents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_type: sourceType, source_path: sourcePath })
      });
      if (!res.ok) throw new Error("Ingestion failed");
      const data = await res.json();
      setStatus(`Job started: ${data.job_id}`);
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel animate-slide-up" style={{ padding: '20px' }}>
      <h3 style={{ marginBottom: '15px', color: 'var(--neon-amber)' }}>Data Ingestion</h3>
      
      <form onSubmit={handleIngest} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <select 
          value={sourceType} 
          onChange={e => setSourceType(e.target.value)}
          style={{ background: 'rgba(0,0,0,0.4)', color: 'white', padding: '8px', borderRadius: '8px', border: '1px solid var(--panel-border)' }}
        >
          <option value="icij_offshore_leaks">ICIJ Offshore Leaks</option>
          <option value="enron_emails">Enron Emails</option>
          <option value="court_judgment">Court Judgments</option>
        </select>
        
        <input 
          type="text" 
          placeholder="Path to data file/folder" 
          value={sourcePath} 
          onChange={e => setSourcePath(e.target.value)} 
          required 
        />
        
        <button type="submit" disabled={loading} style={{ background: 'rgba(245, 158, 11, 0.2)', color: 'var(--neon-amber)', borderColor: 'var(--neon-amber)' }}>
          {loading ? 'Submitting...' : 'Ingest Data'}
        </button>
      </form>
      
      {status && (
        <div style={{ marginTop: '10px', fontSize: '12px', color: status.startsWith('Error') ? '#ef4444' : 'var(--neon-emerald)' }}>
          {status}
        </div>
      )}
    </div>
  );
}
