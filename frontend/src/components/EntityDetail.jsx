import React, { useState, useEffect } from 'react';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function EntityDetail({ entityId, onClose }) {
  const [entity, setEntity] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchEntity() {
      setLoading(true);
      try {
        const res = await fetch(`${BASE_URL}/api/graph/entities/${entityId}`);
        if (res.ok) {
          const data = await res.json();
          setEntity(data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchEntity();
  }, [entityId]);

  return (
    <div className="glass-panel animate-slide-left" style={{ padding: '20px', position: 'relative' }}>
      <button 
        onClick={onClose} 
        style={{ position: 'absolute', top: '10px', right: '10px', background: 'transparent', border: 'none', padding: '5px' }}
      >
        ✕
      </button>
      <h3 style={{ marginBottom: '15px', color: 'var(--neon-cyan)' }}>Entity Details</h3>
      
      {loading ? (
        <p style={{ color: 'var(--text-muted)' }}>Loading...</p>
      ) : entity ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '14px' }}>
          <div><strong>ID:</strong> <span style={{ color: 'var(--text-muted)' }}>{entity.entity_id}</span></div>
          <div><strong>Name:</strong> {entity.name}</div>
          <div>
            <strong>Type:</strong> 
            <span style={{ 
              marginLeft: '8px', 
              padding: '2px 8px', 
              background: 'rgba(139, 92, 246, 0.2)', 
              color: 'var(--neon-purple)',
              borderRadius: '12px',
              fontSize: '12px'
            }}>
              {entity.kind}
            </span>
          </div>
          <div><strong>Confidence:</strong> {entity.confidence?.toFixed(2) || 'N/A'}</div>
        </div>
      ) : (
        <p style={{ color: '#ef4444' }}>Failed to load entity details.</p>
      )}
    </div>
  );
}
