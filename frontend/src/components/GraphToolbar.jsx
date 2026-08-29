import React from 'react';
import { KIND_COLORS } from './GraphViewer';

export default function GraphToolbar({ 
  allKinds, 
  visibleKinds, 
  toggleKind, 
  onExportPng, 
  onFit, 
  physicsEnabled, 
  togglePhysics 
}) {
  const isKindVisible = (kind) => visibleKinds === null || visibleKinds.includes(kind);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      position: 'absolute',
      top: '66px',
      left: '24px',
      zIndex: 25,
    }}>
      {/* Controls Container */}
      <div className="glass-panel" style={{
        display: 'flex',
        gap: '8px',
        padding: '8px',
      }}>
        <button onClick={onFit} title="Fit to Screen" style={{ width: '36px', height: '36px', padding: 0 }}>
          🔲
        </button>
        <button onClick={togglePhysics} title={physicsEnabled ? "Disable Physics (Freeze)" : "Enable Physics"} style={{ width: '36px', height: '36px', padding: 0 }}>
          {physicsEnabled ? '🛑' : '▶️'}
        </button>
        <button onClick={onExportPng} title="Export as PNG" style={{ width: '36px', height: '36px', padding: 0 }}>
          📸
        </button>
      </div>

      {/* Filter Container */}
      {allKinds.length > 1 && (
        <div className="glass-panel" style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
          padding: '12px',
          maxWidth: '200px'
        }}>
          <div style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Filters</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {allKinds.map(kind => {
              const style = KIND_COLORS[kind] || KIND_COLORS.default;
              const active = isKindVisible(kind);
              return (
                <button
                  key={kind}
                  onClick={() => toggleKind(kind)}
                  className={`filter-chip ${active ? 'active' : ''}`}
                  title={`${active ? 'Hide' : 'Show'} ${style.label} entities`}
                  style={{ padding: '4px 8px', fontSize: '11px' }}
                >
                  <span style={{
                    width: '8px', height: '8px', borderRadius: '50%',
                    background: active ? style.border : 'var(--text-dim)',
                    display: 'inline-block',
                  }} />
                  {style.label}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
