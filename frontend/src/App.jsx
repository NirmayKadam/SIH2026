import React, { useState } from 'react';
import GraphViewer from './components/GraphViewer';
import QueryBox from './components/QueryBox';
import EntityDetail from './components/EntityDetail';
import AnalyticsPanel from './components/AnalyticsPanel';
import IngestionPanel from './components/IngestionPanel';

export default function App() {
  const [selectedEntityId, setSelectedEntityId] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [queryResult, setQueryResult] = useState(null);

  const handleQuerySuccess = (data, intent, explanation) => {
    setQueryResult({ intent, data, explanation });
    if (intent === 'NEIGHBORS_WITHIN_HOPS' && data.nodes) {
      setGraphData({ nodes: data.nodes, edges: data.edges || [] });
    }
  };

  return (
    <>
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}>
        <GraphViewer data={graphData} onNodeClick={setSelectedEntityId} />
      </div>

      <div style={{ position: 'absolute', top: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: 10, width: '600px' }}>
        <QueryBox onQuerySuccess={handleQuerySuccess} />
      </div>

      {selectedEntityId && (
        <div style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 10, width: '350px' }}>
          <EntityDetail entityId={selectedEntityId} onClose={() => setSelectedEntityId(null)} />
        </div>
      )}

      <div style={{ position: 'absolute', bottom: '20px', left: '20px', zIndex: 10, width: '350px' }}>
        <AnalyticsPanel />
      </div>

      <div style={{ position: 'absolute', bottom: '20px', right: '20px', zIndex: 10, width: '300px' }}>
        <IngestionPanel />
      </div>
    </>
  );
}
