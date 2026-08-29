import React, { useState, useEffect } from 'react';
import { searchEntities, getShortestPath } from '../api/client';
import { useToast } from './ToastProvider';

export default function PathFinderPanel({ onPathFound }) {
  const [sourceQuery, setSourceQuery] = useState('');
  const [targetQuery, setTargetQuery] = useState('');
  const [sourceEntity, setSourceEntity] = useState(null);
  const [targetEntity, setTargetEntity] = useState(null);
  
  const [sourceResults, setSourceResults] = useState([]);
  const [targetResults, setTargetResults] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (sourceQuery.length < 2) {
      setSourceResults([]);
      return;
    }
    const delay = setTimeout(() => {
      searchEntities(sourceQuery, 5).then(res => setSourceResults(res || [])).catch(console.error);
    }, 300);
    return () => clearTimeout(delay);
  }, [sourceQuery]);

  useEffect(() => {
    if (targetQuery.length < 2) {
      setTargetResults([]);
      return;
    }
    const delay = setTimeout(() => {
      searchEntities(targetQuery, 5).then(res => setTargetResults(res || [])).catch(console.error);
    }, 300);
    return () => clearTimeout(delay);
  }, [targetQuery]);

  const handleFindPath = async () => {
    if (!sourceEntity || !targetEntity) return;
    setLoading(true);
    try {
      const pathData = await getShortestPath(sourceEntity.entity_id || sourceEntity.id, targetEntity.entity_id || targetEntity.id);
      if (!pathData) {
        toast.warning('No path found between these entities.');
      } else {
        toast.success(`Found path with ${pathData.edges.length} hops`);
        if (onPathFound) onPathFound(pathData);
      }
    } catch (err) {
      toast.error(`Error finding path: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <h3 style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-main)', textTransform: 'uppercase' }}>
        🔍 Shortest Path
      </h3>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {/* Source Entity */}
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            placeholder="Source Entity..."
            value={sourceEntity ? sourceEntity.name : sourceQuery}
            onChange={(e) => {
              setSourceQuery(e.target.value);
              if (sourceEntity) setSourceEntity(null);
            }}
            style={{ 
              width: '100%', padding: '8px', fontSize: '12px',
              border: sourceEntity ? '1px solid var(--neon-emerald)' : '1px solid var(--panel-border)'
            }}
          />
          {!sourceEntity && sourceResults.length > 0 && (
            <div style={{
              position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 10,
              background: 'var(--bg-card)', border: '1px solid var(--panel-border)',
              borderRadius: '0 0 6px 6px', maxHeight: '150px', overflowY: 'auto'
            }}>
              {sourceResults.map(r => (
                <div 
                  key={r.entity_id || r.id}
                  onClick={() => {
                    setSourceEntity(r);
                    setSourceQuery(r.name);
                    setSourceResults([]);
                  }}
                  style={{ padding: '6px 8px', fontSize: '12px', cursor: 'pointer', borderBottom: '1px solid var(--panel-border)' }}
                >
                  {r.name} <span style={{ color: 'var(--text-dim)', fontSize: '10px' }}>({r.kind})</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Target Entity */}
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            placeholder="Target Entity..."
            value={targetEntity ? targetEntity.name : targetQuery}
            onChange={(e) => {
              setTargetQuery(e.target.value);
              if (targetEntity) setTargetEntity(null);
            }}
            style={{ 
              width: '100%', padding: '8px', fontSize: '12px',
              border: targetEntity ? '1px solid var(--neon-cyan)' : '1px solid var(--panel-border)'
            }}
          />
          {!targetEntity && targetResults.length > 0 && (
            <div style={{
              position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 10,
              background: 'var(--bg-card)', border: '1px solid var(--panel-border)',
              borderRadius: '0 0 6px 6px', maxHeight: '150px', overflowY: 'auto'
            }}>
              {targetResults.map(r => (
                <div 
                  key={r.entity_id || r.id}
                  onClick={() => {
                    setTargetEntity(r);
                    setTargetQuery(r.name);
                    setTargetResults([]);
                  }}
                  style={{ padding: '6px 8px', fontSize: '12px', cursor: 'pointer', borderBottom: '1px solid var(--panel-border)' }}
                >
                  {r.name} <span style={{ color: 'var(--text-dim)', fontSize: '10px' }}>({r.kind})</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <button 
          onClick={handleFindPath}
          disabled={!sourceEntity || !targetEntity || loading}
          style={{
            background: 'var(--btn-bg)',
            color: (sourceEntity && targetEntity) ? 'var(--neon-emerald)' : 'var(--text-dim)',
            borderColor: (sourceEntity && targetEntity) ? 'var(--neon-emerald)' : 'var(--panel-border)',
            padding: '8px',
            marginTop: '4px',
            fontSize: '13px'
          }}
        >
          {loading ? 'Searching...' : 'Find Path'}
        </button>
      </div>
    </div>
  );
}
