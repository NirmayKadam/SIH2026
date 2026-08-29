import React, { useState } from 'react';
import { useToast } from './ToastProvider';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function IngestionPanel() {
  const [sourceType, setSourceType] = useState('icij_offshore_leaks');
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const handleIngest = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      toast.warning('Please select a file first.');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('source_type', sourceType);
      formData.append('file', selectedFile);

      const res = await fetch(`${BASE_URL}/api/ingestion/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (!res.ok) {
        const errorText = await res.text().catch(() => 'Unknown error');
        throw new Error(`Ingestion failed (${res.status}): ${errorText.slice(0, 100)}`);
      }
      const data = await res.json();
      toast.success(`Ingestion job started: ${data.job_id}`);
      setSelectedFile(null);
      if (e.target) e.target.reset(); // clear file input visually
    } catch (err) {
      toast.error(`Ingestion failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '18px', width: '100%' }}>
      <h3 style={{ marginBottom: '14px', fontSize: '14px', fontWeight: '700', color: 'var(--neon-amber)', letterSpacing: '0.5px' }}>
        📥 DATA INGESTION
      </h3>
      
      <form onSubmit={handleIngest} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <select 
          value={sourceType} 
          onChange={e => setSourceType(e.target.value)}
          disabled={loading}
          style={{ padding: '8px 10px', fontSize: '12px', borderRadius: '8px' }}
        >
          <option value="icij_offshore_leaks">ICIJ Offshore Leaks (CSV)</option>
          <option value="enron_emails">Enron Emails (Mbox)</option>
          <option value="court_judgment">Court Judgments (PDF)</option>
        </select>
        
        <input 
          type="file" 
          onChange={e => setSelectedFile(e.target.files[0] || null)} 
          required 
          disabled={loading}
          style={{ padding: '8px', fontSize: '12px' }}
        />
        
        <button 
          type="submit" 
          disabled={loading || !selectedFile} 
          style={{ 
            background: loading ? 'rgba(245, 158, 11, 0.1)' : 'rgba(245, 158, 11, 0.2)', 
            color: 'var(--neon-amber)', 
            borderColor: 'var(--neon-amber)' 
          }}
        >
          {loading ? (
            <>
              <span style={{
                width: '12px', height: '12px', border: '2px solid var(--panel-border)',
                borderTopColor: 'var(--neon-amber)', borderRadius: '50%',
                animation: 'spin 0.8s linear infinite', display: 'inline-block',
              }} />
              Uploading...
            </>
          ) : 'Upload & Ingest'}
        </button>
      </form>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
