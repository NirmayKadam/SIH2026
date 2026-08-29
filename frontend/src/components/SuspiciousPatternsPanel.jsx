import React, { useState, useEffect } from 'react';
import { getSuspiciousPatterns } from '../api/client';
import { useToast } from './ToastProvider';

const PATTERN_ICONS = {
  'shell_company_cluster': '🏢',
  'high_betweenness_facilitator': '🕸️',
  'circular_flow': '🔄',
};

const PATTERN_LABELS = {
  'shell_company_cluster': 'Shell Company Cluster',
  'high_betweenness_facilitator': 'Network Facilitator',
  'circular_flow': 'Circular Flow',
};

function riskColor(score) {
  if (score >= 0.7) return '#ef4444';
  if (score >= 0.4) return '#f59e0b';
  return '#10b981';
}

function riskLabel(score) {
  if (score >= 0.7) return 'HIGH';
  if (score >= 0.4) return 'MEDIUM';
  return 'LOW';
}

export default function SuspiciousPatternsPanel({ onSelectEntity }) {
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedIdx, setExpandedIdx] = useState(null);
  const toast = useToast();

  useEffect(() => {
    async function fetchPatterns() {
      setLoading(true);
      try {
        const data = await getSuspiciousPatterns();
        setPatterns(data);
      } catch (err) {
        toast.error('Failed to load suspicious patterns');
      } finally {
        setLoading(false);
      }
    }
    fetchPatterns();
  }, []);

  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '18px', width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#ef4444', letterSpacing: '0.5px' }}>
          ⚠️ THREAT DETECTION
        </h3>
        <span style={{
          fontSize: '10px',
          fontWeight: '600',
          color: 'var(--text-dim)',
          background: 'rgba(239, 68, 68, 0.1)',
          padding: '2px 8px',
          borderRadius: '10px',
          border: '1px solid rgba(239, 68, 68, 0.2)',
        }}>
          {patterns.length} found
        </span>
      </div>

      {loading ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '13px' }}>
          <span className="spinner" style={{
            width: '14px', height: '14px', border: '2px solid var(--panel-border)',
            borderTopColor: '#ef4444', borderRadius: '50%',
            animation: 'spin 0.8s linear infinite', display: 'inline-block',
          }} />
          Scanning network for anomalies...
        </div>
      ) : patterns.length === 0 ? (
        <p style={{ fontSize: '12px', color: 'var(--text-dim)' }}>No suspicious patterns detected. Ingest data first.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflowY: 'auto' }}>
          {patterns.map((p, idx) => (
            <div
              key={idx}
              onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
              style={{
                padding: '10px 12px',
                background: 'rgba(239, 68, 68, 0.04)',
                borderRadius: '10px',
                border: `1px solid ${expandedIdx === idx ? 'rgba(239, 68, 68, 0.3)' : 'rgba(255,255,255,0.05)'}`,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              {/* Header Row */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '16px' }}>{PATTERN_ICONS[p.pattern_type] || '⚡'}</span>
                  <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-main)' }}>
                    {PATTERN_LABELS[p.pattern_type] || p.pattern_type}
                  </span>
                </div>
                <span style={{
                  fontSize: '10px',
                  fontWeight: '700',
                  color: riskColor(p.risk_score),
                  background: `${riskColor(p.risk_score)}18`,
                  padding: '2px 8px',
                  borderRadius: '4px',
                  letterSpacing: '0.5px',
                }}>
                  {riskLabel(p.risk_score)} ({(p.risk_score * 100).toFixed(0)}%)
                </span>
              </div>

              {/* Expanded Details */}
              {expandedIdx === idx && (
                <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--panel-border)' }}>
                  <p style={{ fontSize: '11.5px', color: 'var(--text-muted)', lineHeight: '1.5', marginBottom: '8px' }}>
                    {p.description}
                  </p>

                  {/* Detail pills */}
                  {p.details && Object.keys(p.details).length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '8px' }}>
                      {Object.entries(p.details).map(([key, value]) => (
                        <span key={key} style={{
                          fontSize: '10px',
                          padding: '2px 6px',
                          background: 'rgba(255,255,255,0.05)',
                          borderRadius: '4px',
                          color: 'var(--text-dim)',
                        }}>
                          {key.replace(/_/g, ' ')}: <span style={{ color: 'var(--text-main)' }}>{value}</span>
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Involved entities */}
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {p.involved_entity_ids.slice(0, 5).map(id => (
                      <button
                        key={id}
                        onClick={(e) => { e.stopPropagation(); onSelectEntity(id); }}
                        style={{
                          fontSize: '10px',
                          padding: '3px 8px',
                          borderRadius: '6px',
                          background: 'rgba(6, 182, 212, 0.1)',
                          border: '1px solid rgba(6, 182, 212, 0.2)',
                          color: 'var(--neon-cyan)',
                          cursor: 'pointer',
                          fontFamily: 'JetBrains Mono',
                        }}
                      >
                        {id.length > 20 ? id.substring(0, 20) + '…' : id}
                      </button>
                    ))}
                    {p.involved_entity_ids.length > 5 && (
                      <span style={{ fontSize: '10px', color: 'var(--text-dim)', padding: '3px 4px' }}>
                        +{p.involved_entity_ids.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
