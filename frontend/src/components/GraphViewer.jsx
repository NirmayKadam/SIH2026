import React, { useEffect, useRef, useMemo, useImperativeHandle, forwardRef } from 'react';
import { Network } from 'vis-network';

const KIND_COLORS = {
  person: { bg: '#1e1b4b', border: '#818cf8', highlight: '#a5b4fc', shadow: 'rgba(129, 140, 248, 0.4)', label: 'Person', icon: '👤' },
  organization: { bg: '#082f49', border: '#38bdf8', highlight: '#7dd3fc', shadow: 'rgba(56, 189, 248, 0.4)', label: 'Organization', icon: '🏢' },
  account: { bg: '#064e3b', border: '#34d399', highlight: '#6ee7b7', shadow: 'rgba(52, 211, 153, 0.4)', label: 'Account', icon: '💳' },
  location: { bg: '#451a03', border: '#fb923c', highlight: '#fdba74', shadow: 'rgba(251, 146, 60, 0.4)', label: 'Location', icon: '📍' },
  event: { bg: '#4c0519', border: '#fb7185', highlight: '#fda4af', shadow: 'rgba(251, 113, 133, 0.4)', label: 'Event', icon: '📅' },
  vehicle: { bg: '#3b0764', border: '#c084fc', highlight: '#d8b4fe', shadow: 'rgba(192, 132, 252, 0.4)', label: 'Vehicle', icon: '🚗' },
  phone_number: { bg: '#134e4a', border: '#2dd4bf', highlight: '#5eead4', shadow: 'rgba(45, 212, 191, 0.4)', label: 'Phone', icon: '📱' },
  default: { bg: '#18181b', border: '#a1a1aa', highlight: '#e4e4e7', shadow: 'rgba(161, 161, 170, 0.3)', label: 'Unknown', icon: '❓' }
};

const COMMUNITY_PALETTE = [
  { bg: '#312e81', border: '#6366f1' }, // Indigo
  { bg: '#064e3b', border: '#10b981' }, // Emerald
  { bg: '#701a75', border: '#d946ef' }, // Fuchsia
  { bg: '#7c2d12', border: '#f97316' }, // Orange
  { bg: '#14532d', border: '#22c55e' }, // Green
  { bg: '#1e3a8a', border: '#3b82f6' }, // Blue
  { bg: '#4c1d95', border: '#8b5cf6' }, // Violet
  { bg: '#831843', border: '#f43f5e' }, // Rose
];

export { KIND_COLORS };

const GraphViewer = forwardRef(function GraphViewer({ data, onNodeClick, selectedEntityId, visibleKinds, physicsEnabled = true, communityMap = new Map() }, ref) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  // Expose exportToPng method to parent via ref
  useImperativeHandle(ref, () => ({
    exportToPng() {
      if (!networkRef.current) return null;
      try {
        const canvas = containerRef.current?.querySelector('canvas');
        if (canvas) {
          return canvas.toDataURL('image/png');
        }
      } catch (err) {
        console.error('Failed to export graph to PNG:', err);
      }
      return null;
    },
    fitToScreen() {
      if (networkRef.current) {
        networkRef.current.fit({ animation: { duration: 500, easingFunction: 'easeInOutQuad' } });
      }
    }
  }), []);

  // Merge same_as nodes
  const processedData = useMemo(() => {
    if (!data || !data.nodes) return { nodes: [], edges: [] };
    
    const parent = new Map();
    const find = (i) => {
      if (!parent.has(i)) parent.set(i, i);
      if (parent.get(i) === i) return i;
      const p = find(parent.get(i));
      parent.set(i, p);
      return p;
    };
    const union = (i, j) => {
      const rootI = find(i);
      const rootJ = find(j);
      if (rootI !== rootJ) parent.set(rootI, rootJ);
    };

    (data.edges || []).forEach(e => {
      if (e.kind === 'same_as') union(e.source, e.target);
    });

    const aliasMap = new Map();
    const aliasCounts = new Map();
    (data.nodes || []).forEach(n => {
      const root = find(n.id);
      aliasMap.set(n.id, root);
      if (n.id !== root) {
        aliasCounts.set(root, (aliasCounts.get(root) || 0) + 1);
      }
    });

    const newNodes = (data.nodes || []).filter(n => n.id === aliasMap.get(n.id)).map(n => {
      const aliases = aliasCounts.get(n.id) || 0;
      return { ...n, name: aliases > 0 ? `${n.name} (+${aliases})` : n.name };
    });

    const newEdges = [];
    const edgeSeen = new Set();
    (data.edges || []).forEach(e => {
      if (e.kind === 'same_as') return;
      const source = aliasMap.get(e.source) || e.source;
      const target = aliasMap.get(e.target) || e.target;
      if (source === target) return; // drop self-loops from merge
      
      const key = `${source}-${target}-${e.kind}`;
      if (!edgeSeen.has(key)) {
        edgeSeen.add(key);
        newEdges.push({ ...e, source, target });
      }
    });

    return { nodes: newNodes, edges: newEdges };
  }, [data]);

  // Filter nodes by visible kinds
  const filteredData = useMemo(() => {
    if (!visibleKinds || visibleKinds.length === 0) return processedData;

    const visibleSet = new Set(visibleKinds.map(k => k.toLowerCase()));
    const filteredNodes = (processedData.nodes || []).filter(n => {
      const kind = (n.kind || '').toLowerCase();
      return visibleSet.has(kind) || visibleSet.has('default');
    });

    const nodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = (processedData.edges || []).filter(e =>
      nodeIds.has(e.source) && nodeIds.has(e.target)
    );

    return { nodes: filteredNodes, edges: filteredEdges };
  }, [processedData, visibleKinds]);

  useEffect(() => {
    if (!containerRef.current) return;

    const visNodes = (filteredData.nodes || []).map(n => {
      const kind = (n.kind || '').toLowerCase();
      
      let style = KIND_COLORS[kind] || KIND_COLORS.default;
      
      // Override with community colors if available
      if (communityMap && communityMap.has(n.id)) {
        const commIdx = communityMap.get(n.id) % COMMUNITY_PALETTE.length;
        const commColor = COMMUNITY_PALETTE[commIdx];
        style = { ...style, bg: commColor.bg, border: commColor.border };
      }

      const isSelected = n.id === selectedEntityId;

      return {
        id: n.id,
        label: n.name || n.id,
        group: n.kind,
        title: `<b>${n.name || n.id}</b><br/>Type: ${n.kind || 'Unknown'}<br/>ID: ${n.id}${communityMap.has(n.id) ? `<br/>Community: ${communityMap.get(n.id)}` : ''}`,
        shape: 'dot',
        size: isSelected ? 28 : (n.confidence > 0.8 ? 24 : 18),
        font: { 
          color: '#f8fafc', 
          size: 13, 
          face: 'Plus Jakarta Sans, sans-serif',
          background: 'rgba(0,0,0,0.6)',
          strokeWidth: 0
        },
        borderWidth: isSelected ? 4 : 2,
        color: {
          background: style.bg,
          border: isSelected ? '#ffffff' : style.border,
          highlight: { 
            background: style.highlight || style.border, 
            border: '#ffffff' 
          }
        },
        shadow: {
          enabled: true,
          color: style.shadow || 'rgba(0,0,0,0.5)',
          size: isSelected ? 18 : 8
        }
      };
    });

    const visEdges = (filteredData.edges || []).map(e => ({
      from: e.source,
      to: e.target,
      label: (e.kind || '').replace(/_/g, ' '),
      font: { 
        color: '#94a3b8', 
        size: 11, 
        align: 'middle', 
        strokeWidth: 0,
        background: 'rgba(0,0,0,0.6)'
      },
      color: { 
        color: 'rgba(148, 163, 184, 0.3)', 
        highlight: '#38bdf8',
        hover: '#818cf8'
      },
      width: 1.5,
      smooth: { type: 'continuous' }
    }));

    const options = {
      nodes: {
        scaling: { min: 16, max: 32 }
      },
      edges: {
        arrows: { to: { enabled: true, scaleFactor: 0.6 } },
        selectionWidth: 2.5
      },
      physics: {
        enabled: physicsEnabled,
        solver: 'forceAtlas2Based',
        forceAtlas2Based: {
          gravitationalConstant: -100,
          centralGravity: 0.015,
          springLength: 160,
          springConstant: 0.05,
          damping: 0.8
        },
        stabilization: { iterations: 120 }
      },
      interaction: {
        hover: true,
        tooltipDelay: 150,
        zoomView: true,
        dragView: true
      }
    };

    const networkData = { nodes: visNodes, edges: visEdges };

    if (networkRef.current) {
      networkRef.current.setData(networkData);
      networkRef.current.setOptions({ physics: { enabled: physicsEnabled } });
    } else {
      networkRef.current = new Network(containerRef.current, networkData, options);
      networkRef.current.on('click', (params) => {
        if (params.nodes && params.nodes.length > 0) {
          // Find the original node ID since we might have passed a merged ID
          onNodeClick(params.nodes[0]);
        }
      });
    }
  }, [filteredData, selectedEntityId, onNodeClick, physicsEnabled]);

  // Compute which entity kinds are present in the current data
  const activeKinds = useMemo(() => {
    const kinds = new Set();
    (data.nodes || []).forEach(n => {
      const k = (n.kind || '').toLowerCase();
      if (KIND_COLORS[k]) kinds.add(k);
    });
    return Array.from(kinds);
  }, [data.nodes]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {(!filteredData.nodes || filteredData.nodes.length === 0) && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
          color: 'var(--text-dim)',
          zIndex: 1,
          pointerEvents: 'none'
        }}>
          <div style={{ fontSize: '40px', marginBottom: '12px', opacity: 0.6 }}>🕸️</div>
          <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-muted)', marginBottom: '6px' }}>No active graph view</div>
          <div style={{ fontSize: '13px', lineHeight: '1.6', maxWidth: '320px' }}>
            Use the search bar above to find entities,<br />
            or switch to the <strong>Ingest Source</strong> tab to load data.
          </div>
        </div>
      )}
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

      {/* Floating Graph Legend */}
      {activeKinds.length > 0 && (
        <div style={{
          position: 'absolute',
          bottom: '12px',
          right: '12px',
          zIndex: 5,
          background: 'var(--bg-card)',
          backdropFilter: 'blur(12px)',
          border: '1px solid var(--panel-border)',
          borderRadius: '10px',
          padding: '10px 14px',
          display: 'flex',
          flexDirection: 'column',
          gap: '5px',
          boxShadow: 'var(--glass-shadow)',
        }}>
          <div style={{ fontSize: '10px', fontWeight: '700', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '2px' }}>
            Legend
          </div>
          {activeKinds.map(k => {
            const style = KIND_COLORS[k];
            return (
              <div key={k} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{
                  width: '10px', height: '10px', borderRadius: '50%',
                  background: style.border, display: 'inline-block',
                  boxShadow: `0 0 6px ${style.shadow}`,
                }} />
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  {style.icon} {style.label}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
});

export default GraphViewer;
