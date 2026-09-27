import React, { useState, useEffect } from 'react';

export default function GeoMapPage() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '24px 32px', borderBottom: '1px solid var(--panel-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--text-main)', marginBottom: '8px' }}>Geo Intelligence</h1>
          <p style={{ color: 'var(--text-muted)' }}>Cross-border entity mapping and structural risk visualization.</p>
        </div>
        <div className="glass-panel" style={{ padding: '8px 16px', borderRadius: '8px', display: 'flex', gap: '16px' }}>
           <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }}></div>
              <span style={{ fontSize: '12px', color: 'var(--text-main)' }}>High Risk</span>
           </div>
           <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--neon-amber)' }}></div>
              <span style={{ fontSize: '12px', color: 'var(--text-main)' }}>Moderate</span>
           </div>
        </div>
      </div>

      <div style={{ flex: 1, position: 'relative', background: '#0a101f' }}>
        {loading ? (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px' }}>
             <div style={{ width: '48px', height: '48px', border: '3px solid var(--panel-border)', borderTopColor: 'var(--neon-cyan)', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
             <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Connecting to SAT-INT telemetry...</span>
          </div>
        ) : (
          <>
            {/* World Map Background Simulation */}
            <div style={{
              position: 'absolute', inset: 0,
              background: 'url("https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg") center/cover no-repeat',
              opacity: 0.2,
              filter: 'invert(1) hue-rotate(180deg)'
            }} />
            
            {/* Nodes on Map */}
            <div className="pulse-node" style={{ top: '35%', left: '20%', background: '#ef4444', '--pulse-color': 'rgba(239, 68, 68, 0.5)' }}>
               <span className="node-label">Panama (Offshore Hub)</span>
            </div>
            
            <div className="pulse-node" style={{ top: '25%', left: '45%', background: 'var(--neon-amber)', '--pulse-color': 'rgba(245, 158, 11, 0.5)' }}>
               <span className="node-label">London (Facilitator)</span>
            </div>
            
            <div className="pulse-node" style={{ top: '45%', left: '70%', background: '#ef4444', '--pulse-color': 'rgba(239, 68, 68, 0.5)' }}>
               <span className="node-label">Dubai (Money Flow)</span>
            </div>

            <div className="pulse-node" style={{ top: '40%', left: '60%', background: 'var(--neon-cyan)', '--pulse-color': 'rgba(6, 182, 212, 0.5)' }}>
               <span className="node-label">Cyprus</span>
            </div>

            {/* Simulated Edge SVG connecting them */}
            <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 1 }}>
               <path d="M 20vw 35vh Q 32vw 15vh 45vw 25vh" fill="transparent" stroke="rgba(245, 158, 11, 0.4)" strokeWidth="2" strokeDasharray="5,5" className="animated-path" />
               <path d="M 45vw 25vh Q 52vw 35vh 60vw 40vh" fill="transparent" stroke="rgba(6, 182, 212, 0.4)" strokeWidth="2" strokeDasharray="5,5" className="animated-path" />
               <path d="M 60vw 40vh Q 65vw 42vh 70vw 45vh" fill="transparent" stroke="rgba(239, 68, 68, 0.4)" strokeWidth="2" strokeDasharray="5,5" className="animated-path" />
            </svg>
          </>
        )}
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes dash { to { stroke-dashoffset: -20; } }
        .animated-path {
           animation: dash 1s linear infinite;
        }
        .pulse-node {
           position: absolute;
           width: 12px;
           height: 12px;
           border-radius: 50%;
           transform: translate(-50%, -50%);
           z-index: 2;
           box-shadow: 0 0 0 0 var(--pulse-color);
           animation: pulse 2s infinite;
        }
        .node-label {
           position: absolute;
           top: 16px;
           left: 50%;
           transform: translateX(-50%);
           color: var(--text-main);
           font-size: 11px;
           font-weight: 600;
           white-space: nowrap;
           background: rgba(0,0,0,0.6);
           padding: 2px 6px;
           border-radius: 4px;
        }
        @keyframes pulse {
           0% { box-shadow: 0 0 0 0 var(--pulse-color); }
           70% { box-shadow: 0 0 0 15px rgba(0,0,0,0); }
           100% { box-shadow: 0 0 0 0 rgba(0,0,0,0); }
        }
      `}</style>
    </div>
  );
}
