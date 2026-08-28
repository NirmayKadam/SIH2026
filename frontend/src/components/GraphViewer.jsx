import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network';

const KIND_COLORS = {
  person: { bg: '#1e1b4b', border: '#818cf8', highlight: '#a5b4fc', shadow: 'rgba(129, 140, 248, 0.4)' },
  organization: { bg: '#082f49', border: '#38bdf8', highlight: '#7dd3fc', shadow: 'rgba(56, 189, 248, 0.4)' },
  account: { bg: '#064e3b', border: '#34d399', highlight: '#6ee7b7', shadow: 'rgba(52, 211, 153, 0.4)' },
  location: { bg: '#451a03', border: '#fb923c', highlight: '#fdba74', shadow: 'rgba(251, 146, 60, 0.4)' },
  event: { bg: '#4c0519', border: '#fb7185', highlight: '#fda4af', shadow: 'rgba(251, 113, 133, 0.4)' },
  default: { bg: '#18181b', border: '#a1a1aa', highlight: '#e4e4e7', shadow: 'rgba(161, 161, 170, 0.3)' }
};

export default function GraphViewer({ data, onNodeClick, selectedEntityId }) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const visNodes = (data.nodes || []).map(n => {
      const kind = (n.kind || '').toLowerCase();
      const style = KIND_COLORS[kind] || KIND_COLORS.default;
      const isSelected = n.id === selectedEntityId;

      return {
        id: n.id,
        label: n.name || n.id,
        group: n.kind,
        title: `<b>${n.name || n.id}</b><br/>Type: ${n.kind || 'Unknown'}<br/>ID: ${n.id}`,
        shape: 'dot',
        size: isSelected ? 28 : 20,
        font: { 
          color: '#f8fafc', 
          size: 13, 
          face: 'Plus Jakarta Sans, sans-serif',
          strokeWidth: 2,
          strokeColor: '#000000'
        },
        borderWidth: isSelected ? 4 : 2,
        color: {
          background: style.bg,
          border: isSelected ? '#ffffff' : style.border,
          highlight: { 
            background: style.highlight, 
            border: '#ffffff' 
          }
        },
        shadow: {
          enabled: true,
          color: style.shadow,
          size: isSelected ? 18 : 8
        }
      };
    });

    const visEdges = (data.edges || []).map(e => ({
      from: e.source,
      to: e.target,
      label: (e.kind || '').replace(/_/g, ' '),
      font: { 
        color: '#94a3b8', 
        size: 11, 
        align: 'middle', 
        strokeWidth: 2,
        strokeColor: '#090d16'
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
        solver: 'forceAtlas2Based',
        forceAtlas2Based: {
          gravitationalConstant: -70,
          centralGravity: 0.015,
          springLength: 120,
          springConstant: 0.08,
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
    } else {
      networkRef.current = new Network(containerRef.current, networkData, options);
      networkRef.current.on('click', (params) => {
        if (params.nodes && params.nodes.length > 0) {
          onNodeClick(params.nodes[0]);
        }
      });
    }
  }, [data, selectedEntityId, onNodeClick]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {(!data.nodes || data.nodes.length === 0) && (
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
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>🕸️</div>
          <div style={{ fontSize: '15px', fontWeight: '500' }}>No active graph view</div>
          <div style={{ fontSize: '13px', marginTop: '4px' }}>Select an entity, search, or ask a question to explore the network</div>
        </div>
      )}
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}
