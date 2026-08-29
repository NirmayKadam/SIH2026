import React from 'react';
import SuspiciousPatternsPanel from '../components/SuspiciousPatternsPanel';

export default function ThreatsPage() {
  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px' }}>Threats & Suspicious Patterns</h1>
      <div style={{ maxWidth: '400px' }}>
        <SuspiciousPatternsPanel onSelectEntity={(id) => console.log('Select', id)} />
      </div>
    </div>
  );
}
