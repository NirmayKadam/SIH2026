import React from 'react';
import IngestionPanel from '../components/IngestionPanel';

export default function IngestionPage() {
  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px' }}>Ingestion</h1>
      <div style={{ maxWidth: '400px' }}>
        <IngestionPanel />
      </div>
    </div>
  );
}
