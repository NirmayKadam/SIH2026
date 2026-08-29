import React, { useEffect, useState } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { getGraphStats } from '../api/client';
import SuspiciousPatternsPanel from '../components/SuspiciousPatternsPanel';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function DashboardPage() {
  const [stats, setStats] = useState({ total_nodes: 0, total_edges: 0 });
  
  useEffect(() => {
    getGraphStats().then(setStats).catch(console.error);
  }, []);

  // Backend doesn't provide distribution yet, using placeholder for demo
  const mockDistribution = {
    labels: ['Person', 'Organization', 'Account', 'Location', 'Event'],
    datasets: [{
      data: [300, 50, 100, 40, 10],
      backgroundColor: ['#818cf8', '#38bdf8', '#34d399', '#fb923c', '#fb7185'],
      borderColor: 'rgba(0,0,0,0.1)',
      borderWidth: 1,
    }],
  };

  const chartOptions = {
    plugins: {
      legend: {
        position: 'right',
        labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' } }
      }
    },
    cutout: '70%',
    maintainAspectRatio: false
  };

  return (
    <div style={{ padding: '32px', height: '100%', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: 'var(--text-main)' }}>Overview</h1>
        <span style={{ color: 'var(--text-muted)' }}>System Status & Metrics</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ color: 'var(--text-dim)', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase' }}>Total Entities</div>
          <div style={{ fontSize: '36px', fontWeight: '700', color: 'var(--neon-cyan)', marginTop: '8px' }}>{stats.total_nodes}</div>
        </div>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ color: 'var(--text-dim)', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase' }}>Total Relationships</div>
          <div style={{ fontSize: '36px', fontWeight: '700', color: 'var(--neon-emerald)', marginTop: '8px' }}>{stats.total_edges}</div>
        </div>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ color: 'var(--text-dim)', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase' }}>Active Alerts</div>
          <div style={{ fontSize: '36px', fontWeight: '700', color: 'var(--neon-amber)', marginTop: '8px' }}>12</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', flexGrow: 1 }}>
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-main)', marginBottom: '16px' }}>Entity Distribution</h2>
          <div style={{ flexGrow: 1, position: 'relative', minHeight: '200px' }}>
            <Doughnut data={mockDistribution} options={chartOptions} />
          </div>
        </div>
        
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-main)', marginBottom: '16px' }}>Threat Feed</h2>
          <div style={{ flexGrow: 1, overflowY: 'auto' }}>
            <SuspiciousPatternsPanel onSelectEntity={() => {}} />
          </div>
        </div>
      </div>
    </div>
  );
}
