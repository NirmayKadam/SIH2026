import React, { useState, useEffect } from 'react';
import { getCentrality, getCommunities } from '../api/client';

export default function AnalyticsPanel() {
  const [stats, setStats] = useState({ centrality: [], communities: [] });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchStats() {
      setLoading(true);
      try {
        const [centralityData, communityData] = await Promise.all([
          getCentrality('degree').catch(() => []),
          getCommunities().catch(() => [])
        ]);
        setStats({ 
          centrality: centralityData.slice(0, 5), 
          communities: communityData 
        });
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  return (
    <div className="glass-panel animate-slide-right" style={{ padding: '20px' }}>
      <h3 style={{ marginBottom: '15px', color: 'var(--neon-emerald)' }}>Network Analytics</h3>
      
      {loading ? (
        <p style={{ color: 'var(--text-muted)' }}>Computing...</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <div>
            <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '5px' }}>TOP CENTRAL NODES (DEGREE)</h4>
            {stats.centrality.length > 0 ? (
              <ul style={{ listStyle: 'none', fontSize: '13px' }}>
                {stats.centrality.map(c => (
                  <li key={c.entity_id} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                    <span style={{ color: 'var(--neon-cyan)' }}>{c.entity_id.split('-')[0]}...</span>
                    <span>{c.score.toFixed(2)}</span>
                  </li>
                ))}
              </ul>
            ) : <p style={{ fontSize: '12px' }}>No data</p>}
          </div>

          <div>
            <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '5px' }}>DETECTED COMMUNITIES</h4>
            {stats.communities.length > 0 ? (
              <div style={{ fontSize: '13px' }}>
                {stats.communities.length} total communities.
                Largest has {Math.max(...stats.communities.map(c => c.member_entity_ids?.length || 0))} members.
              </div>
            ) : <p style={{ fontSize: '12px' }}>No data</p>}
          </div>
        </div>
      )}
    </div>
  );
}
