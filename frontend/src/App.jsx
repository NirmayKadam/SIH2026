import React, { useState, useEffect, useCallback } from 'react';
import GraphViewer from './components/GraphViewer';
import QueryBox from './components/QueryBox';
import EntityDetail from './components/EntityDetail';
import AnalyticsPanel from './components/AnalyticsPanel';
import IngestionPanel from './components/IngestionPanel';
import SuspiciousPatternsPanel from './components/SuspiciousPatternsPanel';
import { getCentrality, getEntityNeighbors, getGraphStats } from './api/client';

export default function App() {
  const [selectedEntityId, setSelectedEntityId] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [graphStats, setGraphStats] = useState({ total_nodes: 0, total_edges: 0 });
  const [activeTab, setActiveTab] = useState('analytics'); // 'analytics' | 'ingestion' | 'threats'
  const [theme, setTheme] = useState('dark');
  const [isPanelOpen, setIsPanelOpen] = useState(true);

  // Apply theme to body
  useEffect(() => {
    if (theme === 'light') {
      document.body.classList.add('theme-light');
    } else {
      document.body.classList.remove('theme-light');
    }
  }, [theme]);
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

      {/* Unified Top Navigation Bar */}
      <div className="glass-panel" style={{
        position: 'absolute',
        top: '0',
        left: '0',
        right: '0',
        zIndex: 30,
        borderRadius: '0',
        borderTop: 'none',
        borderLeft: 'none',
        borderRight: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 24px',
        boxShadow: 'var(--glass-shadow)',
        background: 'var(--bg-card)'
      }}>
        {/* Left: Branding & Stats */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '20px' }}>🛡️</span>
            <span style={{ fontWeight: '700', fontSize: '15px', letterSpacing: '0.5px', color: 'var(--text-main)' }}>
              CRIMINAL NETWORK ANALYSIS
            </span>
          </div>
          <div style={{ height: '20px', width: '1px', background: 'var(--panel-border)' }} />
          <div style={{ display: 'flex', gap: '8px' }}>
            <span className="badge-tag">{graphStats.total_nodes} NODES</span>
            <span className="badge-tag">{graphStats.total_edges} EDGES</span>
          </div>
        </div>

        {/* Center: Search */}
        <div style={{ width: 'min(500px, 40vw)' }}>
          <QueryBox 
            onQuerySuccess={handleQuerySuccess} 
            onSelectEntity={handleSelectEntity}
            transparent={true}
          />
        </div>

        {/* Right: Theme Toggle */}
        <div>
          <button 
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            style={{ 
              background: 'rgba(0,0,0,0.05)', 
              border: '1px solid var(--panel-border)', 
              borderRadius: '50%', 
              width: '40px', 
              height: '40px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              fontSize: '18px',
              cursor: 'pointer'
            }}
            title="Toggle Day/Night Mode"
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </div>

      {/* Right Drawer: Entity Detail (if selected) */}
      {selectedEntityId && (
        <div style={{ 
          position: 'absolute', 
          top: '86px', 
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
        width: '360px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        {isPanelOpen ? (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', gap: '6px', flexGrow: 1 }}>
                <button 
                  onClick={() => setActiveTab('analytics')}
                  style={{ 
                    flex: 1, 
                    padding: '6px 12px', 
                    fontSize: '12px',
                    background: activeTab === 'analytics' ? 'rgba(16, 185, 129, 0.2)' : 'var(--btn-bg)',
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
                    background: activeTab === 'ingestion' ? 'rgba(245, 158, 11, 0.2)' : 'var(--btn-bg)',
                    borderColor: activeTab === 'ingestion' ? 'var(--neon-amber)' : 'var(--panel-border)',
                    color: activeTab === 'ingestion' ? 'var(--neon-amber)' : 'var(--text-muted)'
                  }}
                >
                  Ingest Source
                </button>
                <button 
                  onClick={() => setActiveTab('threats')}
                  style={{ 
                    flex: 1, 
                    padding: '6px 12px', 
                    fontSize: '12px',
                    background: activeTab === 'threats' ? 'rgba(239, 68, 68, 0.2)' : 'var(--btn-bg)',
                    borderColor: activeTab === 'threats' ? '#ef4444' : 'var(--panel-border)',
                    color: activeTab === 'threats' ? '#ef4444' : 'var(--text-muted)'
                  }}
                >
                  ⚠ Threats
                </button>
              </div>
              <button 
                onClick={() => setIsPanelOpen(false)}
                style={{ marginLeft: '8px', padding: '6px 10px', fontSize: '12px', background: 'var(--btn-bg)' }}
                title="Collapse Panel"
              >
                ▼
              </button>
            </div>

            {activeTab === 'analytics' ? (
              <AnalyticsPanel onSelectEntity={handleSelectEntity} />
            ) : activeTab === 'threats' ? (
              <SuspiciousPatternsPanel onSelectEntity={handleSelectEntity} />
            ) : (
              <IngestionPanel />
            )}
          </>
        ) : (
          <button 
            className="glass-panel"
            onClick={() => setIsPanelOpen(true)}
            style={{ 
              padding: '10px 16px', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px', 
              borderRadius: '30px', 
              width: 'fit-content' 
            }}
          >
            <span style={{ fontSize: '16px' }}>📊</span> 
            <span>Open Tools</span>
          </button>
        )}
      </div>
    </div>
  );
}
