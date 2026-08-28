import React, { useState, useEffect, useCallback } from 'react';
import GraphViewer from './components/GraphViewer';
import QueryBox from './components/QueryBox';
import EntityDetail from './components/EntityDetail';
import AnalyticsPanel from './components/AnalyticsPanel';
import IngestionPanel from './components/IngestionPanel';
import { getCentrality, getEntityNeighbors, getGraphStats } from './api/client';

export default function App() {
  const [selectedEntityId, setSelectedEntityId] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [graphStats, setGraphStats] = useState({ total_nodes: 0, total_edges: 0 });
  const [activeTab, setActiveTab] = useState('analytics'); // 'analytics' | 'ingestion'

  // Load initial graph cluster from top degree nodes
  const loadInitialGraph = useCallback(async () => {
    try {
      const stats = await getGraphStats().catch(() => ({ total_nodes: 0, total_edges: 0 }));
      setGraphStats(stats);

      const centralNodes = await getCentrality('degree').catch(() => []);
      if (centralNodes && centralNodes.length > 0) {
        const topEntityId = centralNodes[0].entity_id;
        setSelectedEntityId(topEntityId);
        const res = await getEntityNeighbors(topEntityId, 1);
        
        const nodes = [
          { id: res.center.entity_id, name: res.center.name, kind: res.center.kind },
          ...res.nodes.map(n => ({ id: n.entity_id, name: n.name, kind: n.kind }))
        ];
        const edges = res.edges.map(e => ({
          source: e.source_entity_id,
          target: e.target_entity_id,
          kind: e.kind
        }));
        setGraphData({ nodes, edges });
      }
    } catch (err) {
      console.error("Failed to load initial graph view", err);
    }
  }, []);

  useEffect(() => {
    loadInitialGraph();
  }, [loadInitialGraph]);

  const handleSelectEntity = async (entityId) => {
    setSelectedEntityId(entityId);
    try {
      const res = await getEntityNeighbors(entityId, 1);
      const nodes = [
        { id: res.center.entity_id, name: res.center.name, kind: res.center.kind },
        ...res.nodes.map(n => ({ id: n.entity_id, name: n.name, kind: n.kind }))
      ];
      const edges = res.edges.map(e => ({
        source: e.source_entity_id,
        target: e.target_entity_id,
        kind: e.kind
      }));
      setGraphData({ nodes, edges });
    } catch (err) {
      console.error("Failed to fetch neighborhood for entity", entityId, err);
    }
  };

  const handleQuerySuccess = (data, intent, explanation) => {
    if (data && data.nodes) {
      setGraphData({ nodes: data.nodes, edges: data.edges || [] });
    }
  };

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', overflow: 'hidden' }}>
      {/* Background Fullscreen Network Canvas */}
      <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
        <GraphViewer 
          data={graphData} 
          onNodeClick={handleSelectEntity} 
          selectedEntityId={selectedEntityId}
        />
      </div>

      {/* Top Header Bar */}
      <div className="glass-panel app-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '18px' }}>🛡️</span>
          <span style={{ fontWeight: '700', fontSize: '14px', letterSpacing: '0.5px' }}>
            CRIMINAL NETWORK ANALYSIS
          </span>
        </div>
        <div style={{ height: '18px', width: '1px', background: 'var(--panel-border)' }} />
        <div style={{ display: 'flex', gap: '8px' }}>
          <span className="badge-tag">{graphStats.total_nodes} NODES</span>
          <span className="badge-tag">{graphStats.total_edges} EDGES</span>
        </div>
      </div>

      {/* Top Center Query Bar */}
      <div style={{ 
        position: 'absolute', 
        top: '16px', 
        left: '50%', 
        transform: 'translateX(-50%)', 
        zIndex: 20, 
        width: 'min(640px, 90vw)' 
      }}>
        <QueryBox 
          onQuerySuccess={handleQuerySuccess} 
          onSelectEntity={handleSelectEntity}
        />
      </div>

      {/* Right Drawer: Entity Detail (if selected) */}
      {selectedEntityId && (
        <div style={{ 
          position: 'absolute', 
          top: '16px', 
          right: '16px', 
          zIndex: 20, 
          width: '340px' 
        }}>
          <EntityDetail 
            entityId={selectedEntityId} 
            onClose={() => setSelectedEntityId(null)} 
            onExpandNeighborhood={(expanded) => setGraphData(expanded)}
          />
        </div>
      )}

      {/* Bottom Left Drawer: Tabbed Analytics & Ingestion */}
      <div style={{ 
        position: 'absolute', 
        bottom: '16px', 
        left: '16px', 
        zIndex: 20, 
        width: '360px' 
      }}>
        <div style={{ display: 'flex', gap: '6px', marginBottom: '8px' }}>
          <button 
            onClick={() => setActiveTab('analytics')}
            style={{ 
              flex: 1, 
              padding: '6px 12px', 
              fontSize: '12px',
              background: activeTab === 'analytics' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(0,0,0,0.4)',
              borderColor: activeTab === 'analytics' ? 'var(--neon-emerald)' : 'var(--panel-border)',
              color: activeTab === 'analytics' ? 'var(--neon-emerald)' : 'var(--text-muted)'
            }}
          >
            Analytics
          </button>
          <button 
            onClick={() => setActiveTab('ingestion')}
            style={{ 
              flex: 1, 
              padding: '6px 12px', 
              fontSize: '12px',
              background: activeTab === 'ingestion' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(0,0,0,0.4)',
              borderColor: activeTab === 'ingestion' ? 'var(--neon-amber)' : 'var(--panel-border)',
              color: activeTab === 'ingestion' ? 'var(--neon-amber)' : 'var(--text-muted)'
            }}
          >
            Ingest Source
          </button>
        </div>

        {activeTab === 'analytics' ? (
          <AnalyticsPanel onSelectEntity={handleSelectEntity} />
        ) : (
          <IngestionPanel />
        )}
      </div>
    </div>
  );
}
