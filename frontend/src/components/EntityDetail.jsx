import React, { useState, useEffect } from 'react';
import { getEntityDetail, getEntityNeighbors } from '../api/client';

export default function EntityDetail({ entityId, onClose, onExpandNeighborhood }) {
  const [entity, setEntity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [depth, setDepth] = useState(1);

  useEffect(() => {
    async function fetchEntity() {
      setLoading(true);
      try {
        const data = await getEntityDetail(entityId);
        setEntity(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    if (entityId) {
      fetchEntity();
    }
  }, [entityId]);

  const handleExpand = async () => {
    try {
      const res = await getEntityNeighbors(entityId, depth);
      const nodes = [
        { id: res.center.entity_id, name: res.center.name, kind: res.center.kind },
        ...res.nodes.map(n => ({ id: n.entity_id, name: n.name, kind: n.kind }))
      ];
      const edges = res.edges.map(e => ({
        source: e.source_entity_id,
        target: e.target_entity_id,
        kind: e.kind
      }));
      onExpandNeighborhood({ nodes, edges });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '20px', width: '100%', maxWidth: '320px', position: 'relative' }}>
      <button 
        onClick={onClose} 
        style={{ 
          position: 'absolute', 
          top: '12px', 
          right: '12px', 
          background: 'transparent', 
          border: 'none', 
          padding: '4px 8px', 
          color: 'var(--text-muted)',
          fontSize: '14px' 
        }}
      >
        ✕
      </button>

      <div style={{ fontSize: '11px', fontWeight: '700', color: 'var(--neon-cyan)', letterSpacing: '0.5px', marginBottom: '12px', textTransform: 'uppercase' }}>
        Entity Profile
      </div>
      
      {loading ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Retrieving entity details...</p>
      ) : entity ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <div 
              style={{ 
                fontSize: '15px', 
                fontWeight: '700', 
                color: 'var(--text-main)',
                wordBreak: 'break-word',
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}
              title={entity.name}
            >
              {entity.name}
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '8px' }}>
              <span style={{ 
                padding: '2px 8px', 
                background: 'rgba(139, 92, 246, 0.15)', 
                color: '#a78bfa',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: '600',
                textTransform: 'uppercase'
              }}>
                {entity.kind}
              </span>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Confidence: <strong style={{ color: 'var(--neon-emerald)' }}>{(entity.confidence * 100).toFixed(0)}%</strong>
              </span>
            </div>
          </div>

          <div style={{ height: '1px', background: 'var(--panel-border)', margin: '4px 0' }} />

          {/* Metadata Properties */}
          {entity.properties && Object.keys(entity.properties).length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Metadata
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '200px', overflowY: 'auto', paddingRight: '4px' }}>
                {Object.entries(entity.properties).map(([key, value]) => (
                  <div key={key} style={{ fontSize: '12.5px', lineHeight: '1.4', wordBreak: 'break-word' }}>
                    <span style={{ color: 'var(--text-muted)', fontWeight: '500', textTransform: 'capitalize' }}>
                      {key.replace(/_/g, ' ')}: 
                    </span>{' '}
                    <span style={{ color: 'var(--text-main)' }}>{value}</span>
                  </div>
                ))}
              </div>
              <div style={{ height: '1px', background: 'var(--panel-border)', margin: '4px 0' }} />
            </div>
          )}

          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: '8px', fontSize: '12px' }}>
            <div style={{ color: 'var(--text-dim)', marginBottom: '4px' }}>Entity ID:</div>
            <div style={{ fontFamily: 'JetBrains Mono', color: 'var(--text-muted)', wordBreak: 'break-all' }}>{entity.entity_id}</div>
          </div>

          {entity.provenances && entity.provenances.length > 0 && (
            <div>
              <div style={{ fontSize: '11px', fontWeight: '600', color: 'var(--text-dim)', marginBottom: '6px', textTransform: 'uppercase' }}>
                Data Provenance ({entity.provenances.length})
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', maxHeight: '100px', overflowY: 'auto' }}>
                {entity.provenances.map((p, idx) => (
                  <div key={idx} style={{ fontSize: '11px', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.02)', padding: '4px 8px', borderRadius: '4px' }}>
                    <strong style={{ color: 'var(--neon-amber)' }}>{p.source_type}</strong>: {p.source_document_id}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
            <select 
              value={depth} 
              onChange={e => setDepth(Number(e.target.value))}
              style={{ width: '80px', padding: '6px', fontSize: '12px' }}
            >
              <option value={1}>1 hop</option>
              <option value={2}>2 hops</option>
              <option value={3}>3 hops</option>
            </select>
            <button 
              className="primary" 
              onClick={handleExpand}
              style={{ flexGrow: 1, padding: '8px 12px', fontSize: '12px' }}
            >
              Explore Network
            </button>
          </div>
        </div>
      ) : (
        <p style={{ color: 'var(--neon-rose)', fontSize: '13px' }}>Entity not found.</p>
      )}
    </div>
  );
}
