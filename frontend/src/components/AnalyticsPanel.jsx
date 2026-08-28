import React, { useState, useEffect } from 'react';
import { getCentrality, getCommunities, getEntityDetail } from '../api/client';

export default function AnalyticsPanel({ onSelectEntity }) {
  const [stats, setStats] = useState({ centrality: [], communities: [] });
  const [loading, setLoading] = useState(false);
  const [centralityType, setCentralityType] = useState('degree');

  useEffect(() => {
    async function fetchStats() {
      setLoading(true);
      try {
        const [centralityData, communityData] = await Promise.all([
          getCentrality(centralityType).catch(() => []),
          getCommunities().catch(() => [])
        ]);

        // Enrich top 5 entities with real names
        const enriched = await Promise.all(
          centralityData.slice(0, 5).map(async (c) => {
            try {
              const detail = await getEntityDetail(c.entity_id);
              return { ...c, name: detail.name, kind: detail.kind };
            } catch {
              return { ...c, name: c.entity_id, kind: 'unknown' };
            }
          })
        );

        setStats({ 
          centrality: enriched, 
          communities: communityData 
        });
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, [centralityType]);

  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '18px', width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--neon-emerald)', letterSpacing: '0.5px' }}>
          NETWORK ANALYTICS
        </h3>
        <select 
          value={centralityType} 
          onChange={(e) => setCentralityType(e.target.value)}
          style={{ padding: '4px 8px', fontSize: '11px', borderRadius: '6px' }}
        >
          <option value="degree">Degree</option>
          <option value="betweenness">Betweenness</option>
          <option value="pagerank">PageRank</option>
        </select>
      </div>
      
      {loading ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Computing graph metrics...</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: '600', color: 'var(--text-dim)', marginBottom: '8px', textTransform: 'uppercase' }}>
              High-Influence Entities
            </div>
            {stats.centrality.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {stats.centrality.map(c => (
                  <div 
                    key={c.entity_id} 
                    onClick={() => onSelectEntity(c.entity_id)}
                    style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '6px 10px',
                      background: 'rgba(255, 255, 255, 0.03)',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      border: '1px solid transparent',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={e => {
                      e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.4)';
                      e.currentTarget.style.background = 'rgba(6, 182, 212, 0.08)';
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.borderColor = 'transparent';
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
                    }}
                  >
                    <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', marginRight: '8px' }}>
                      <span style={{ fontSize: '12.5px', fontWeight: '600', color: 'var(--text-main)', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                        {c.name || c.entity_id}
                      </span>
                      <span style={{ fontSize: '10.5px', color: 'var(--text-dim)' }}>{c.kind}</span>
                    </div>
                    <span style={{ 
                      fontFamily: 'JetBrains Mono', 
                      fontSize: '11px', 
                      color: 'var(--neon-cyan)',
                      background: 'rgba(6, 182, 212, 0.12)',
                      padding: '2px 6px',
                      borderRadius: '4px'
                    }}>
                      {c.score.toFixed(3)}
                    </span>
                  </div>
                ))}
              </div>
            ) : <p style={{ fontSize: '12px', color: 'var(--text-dim)' }}>No centrality calculated</p>}
          </div>

          <div style={{ borderTop: '1px solid var(--panel-border)', paddingTop: '10px' }}>
            <div style={{ fontSize: '11px', fontWeight: '600', color: 'var(--text-dim)', marginBottom: '6px', textTransform: 'uppercase' }}>
              Community Clusters
            </div>
            {stats.communities.length > 0 ? (
              <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                <span style={{ color: 'var(--text-main)', fontWeight: '600' }}>{stats.communities.length}</span> partitions discovered.<br/>
                Largest cluster contains <span style={{ color: 'var(--neon-emerald)', fontWeight: '600' }}>{Math.max(...stats.communities.map(c => c.member_entity_ids?.length || 0))}</span> members.
              </div>
            ) : <p style={{ fontSize: '12px', color: 'var(--text-dim)' }}>No clusters available</p>}
          </div>
        </div>
      )}
    </div>
  );
}
