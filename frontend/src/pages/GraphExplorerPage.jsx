import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import GraphViewer, { KIND_COLORS } from '../components/GraphViewer';
import QueryBox from '../components/QueryBox';
import EntityDetail from '../components/EntityDetail';
import AnalyticsPanel from '../components/AnalyticsPanel';
import IngestionPanel from '../components/IngestionPanel';
import SuspiciousPatternsPanel from '../components/SuspiciousPatternsPanel';
import PathFinderPanel from '../components/PathFinderPanel';
import GraphToolbar from '../components/GraphToolbar';
import { useToast } from '../components/ToastProvider';
import { getCentrality, getEntityNeighbors, getGraphStats, getCommunities } from '../api/client';

export default function GraphExplorerPage() {
  const [selectedEntityId, setSelectedEntityId] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [graphStats, setGraphStats] = useState({ total_nodes: 0, total_edges: 0 });
  const [activeTab, setActiveTab] = useState('analytics');
  const [isPanelOpen, setIsPanelOpen] = useState(true);
  const [initialLoading, setInitialLoading] = useState(true);
  const [visibleKinds, setVisibleKinds] = useState(null);
  const [physicsEnabled, setPhysicsEnabled] = useState(true);
  const [communityMap, setCommunityMap] = useState(new Map());
  const graphRef = useRef(null);
  const toast = useToast();

  // Collect all unique entity kinds from data
  const allKinds = useMemo(() => {
    const kinds = new Set();
    (graphData.nodes || []).forEach(n => {
      const k = (n.kind || '').toLowerCase();
      if (KIND_COLORS[k]) kinds.add(k);
    });
    return Array.from(kinds);
  }, [graphData.nodes]);

  // Toggle a kind in the filter
  const toggleKind = (kind) => {
    setVisibleKinds(prev => {
      if (prev === null) {
        return allKinds.filter(k => k !== kind);
      }
      if (prev.includes(kind)) {
        const next = prev.filter(k => k !== kind);
        return next.length === 0 ? null : next;
      }
      const next = [...prev, kind];
      return next.length >= allKinds.length ? null : next;
    });
  };

  const isKindVisible = (kind) => {
    return visibleKinds === null || visibleKinds.includes(kind);
  };

  const handleExportPng = () => {
    if (!graphRef.current) return;
    const dataUrl = graphRef.current.exportToPng();
    if (dataUrl) {
      const link = document.createElement('a');
      link.download = `network-graph-${new Date().toISOString().slice(0, 10)}.png`;
      link.href = dataUrl;
      link.click();
      toast.success('Graph exported as PNG');
    } else {
      toast.warning('No graph to export');
    }
  };

  const loadInitialGraph = useCallback(async () => {
    setInitialLoading(true);
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

      const comms = await getCommunities().catch(() => []);
      const cMap = new Map();
      comms.forEach((c, idx) => {
        c.member_entity_ids.forEach(eid => cMap.set(eid, idx));
      });
      setCommunityMap(cMap);

    } catch (err) {
      toast.error(`Failed to load initial graph: ${err.message}`);
    } finally {
      setInitialLoading(false);
    }
  }, [toast]);

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
      toast.error(`Failed to load entity neighborhood: ${err.message}`);
    }
  };

  const handleQuerySuccess = (data, intent, explanation) => {
    if (data && data.nodes) {
      setGraphData({ nodes: data.nodes, edges: data.edges || [] });
      toast.success(`Query resolved (intent: ${intent})`);
    }
  };

  const handlePathFound = (pathData) => {
    if (pathData && pathData.nodes) {
      setGraphData({ nodes: pathData.nodes, edges: pathData.edges || [] });
      setPhysicsEnabled(false); // Stop physics to make the path easier to read
      setTimeout(() => {
        if (graphRef.current) graphRef.current.fitToScreen();
      }, 300);
    }
  };

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
        {initialLoading ? (
          <div style={{
            width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexDirection: 'column', gap: '16px',
          }}>
            <div style={{
              width: '48px', height: '48px', border: '3px solid var(--panel-border)',
              borderTopColor: 'var(--neon-cyan)', borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }} />
            <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Loading network graph...</span>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </div>
        ) : (
          <GraphViewer 
            ref={graphRef}
            data={graphData} 
            onNodeClick={handleSelectEntity} 
            selectedEntityId={selectedEntityId}
            visibleKinds={visibleKinds}
            physicsEnabled={physicsEnabled}
            communityMap={communityMap}
          />
        )}
      </div>

      <GraphToolbar
        allKinds={allKinds}
        visibleKinds={visibleKinds}
        toggleKind={toggleKind}
        onExportPng={handleExportPng}
        onFit={() => graphRef.current?.fitToScreen()}
        physicsEnabled={physicsEnabled}
        togglePhysics={() => setPhysicsEnabled(!physicsEnabled)}
      />

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
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <span className="badge-tag">{graphStats.total_nodes} NODES</span>
            <span className="badge-tag">{graphStats.total_edges} EDGES</span>
          </div>
        </div>

        <div style={{ width: 'min(500px, 40vw)' }}>
          <QueryBox 
            onQuerySuccess={handleQuerySuccess} 
            onSelectEntity={handleSelectEntity}
            transparent={true}
          />
        </div>
        
        {/* Right spacing to balance flex-between */}
        <div style={{ width: '120px' }}></div>
      </div>

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

      {/* Legacy panels temporarily kept on GraphExplorerPage */}
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
                  Ingest
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
                <button 
                  onClick={() => setActiveTab('path')}
                  style={{ 
                    flex: 1, 
                    padding: '6px 12px', 
                    fontSize: '12px',
                    background: activeTab === 'path' ? 'rgba(168, 85, 247, 0.2)' : 'var(--btn-bg)',
                    borderColor: activeTab === 'path' ? 'var(--neon-purple, #a855f7)' : 'var(--panel-border)',
                    color: activeTab === 'path' ? 'var(--neon-purple, #a855f7)' : 'var(--text-muted)'
                  }}
                >
                  Path
                </button>
              </div>
              <button 
                onClick={() => setIsPanelOpen(false)}
                style={{ marginLeft: '8px', padding: '6px 10px', fontSize: '12px', background: 'var(--btn-bg)' }}
              >
                ▼
              </button>
            </div>

            {activeTab === 'analytics' ? (
              <AnalyticsPanel onSelectEntity={handleSelectEntity} />
            ) : activeTab === 'threats' ? (
              <SuspiciousPatternsPanel onSelectEntity={handleSelectEntity} />
            ) : activeTab === 'path' ? (
              <PathFinderPanel onPathFound={handlePathFound} />
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
