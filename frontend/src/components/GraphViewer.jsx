import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network';

export default function GraphViewer({ data, onNodeClick }) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const visNodes = data.nodes.map(n => ({
      id: n.id,
      label: n.name,
      group: n.kind,
      title: `${n.kind || 'Unknown'} Node`,
      shape: 'dot',
      size: 20,
      font: { color: '#ffffff', size: 14, face: 'Inter', strokeWidth: 0 },
      borderWidth: 2,
      color: {
        background: '#1a1a2e',
        border: '#06b6d4',
        highlight: { background: '#252542', border: '#10b981' }
      }
    }));

    const visEdges = data.edges.map(e => ({
      from: e.source,
      to: e.target,
      label: e.kind,
      font: { color: '#94a3b8', size: 10, align: 'middle', strokeWidth: 0 },
      color: { color: 'rgba(255,255,255,0.2)', highlight: '#8b5cf6' },
      width: 1,
      smooth: { type: 'continuous' }
    }));

    const options = {
      nodes: {
        shadow: { enabled: true, color: 'rgba(6,182,212,0.5)', size: 10 }
      },
      edges: {
        arrows: { to: { enabled: true, scaleFactor: 0.5 } }
      },
      physics: {
        barnesHut: { gravitationalConstant: -3000, centralGravity: 0.3, springLength: 150 },
        stabilization: { iterations: 150 }
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
      }
    };

    const networkData = { nodes: visNodes, edges: visEdges };
    
    if (networkRef.current) {
      networkRef.current.setData(networkData);
    } else {
      networkRef.current = new Network(containerRef.current, networkData, options);
      networkRef.current.on('click', (params) => {
        if (params.nodes.length > 0) {
          onNodeClick(params.nodes[0]);
        } else {
          onNodeClick(null);
        }
      });
    }
  }, [data, onNodeClick]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
}
