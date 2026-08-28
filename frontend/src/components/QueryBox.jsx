import React, { useState } from 'react';
import { askQuestion, searchEntities } from '../api/client';

export default function QueryBox({ onQuerySuccess, onSelectEntity, transparent }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resultMsg, setResultMsg] = useState(null);
  const [searchResults, setSearchResults] = useState([]);

  const handleSearch = async (val) => {
    setQuery(val);
    if (val.trim().length >= 2) {
      try {
        const res = await searchEntities(val.trim(), 5);
        setSearchResults(res.entities || []);
      } catch {
        setSearchResults([]);
      }
    } else {
      setSearchResults([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResultMsg(null);
    setSearchResults([]);
    
    try {
      const response = await askQuestion(query);
      setResultMsg({ 
        intent: response.intent, 
        explanation: response.explanation,
        result: response.result 
      });
      onQuerySuccess(response.result, response.intent, response.explanation);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSearchResult = (entity) => {
    setSearchResults([]);
    setQuery(entity.name);
    onSelectEntity(entity.entity_id);
  };

  return (
    <div className={transparent ? "animate-fade-in" : "glass-panel animate-fade-in"} style={{ padding: transparent ? '0' : '14px', width: '100%', position: 'relative' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px' }}>
        <div style={{ flexGrow: 1, position: 'relative' }}>
          <input 
            type="text" 
            placeholder="Ask natural language question or search entity by name..." 
            value={query}
            onChange={e => handleSearch(e.target.value)}
            disabled={loading}
            style={{ width: '100%' }}
          />

          {searchResults.length > 0 && (
            <div style={{
              position: 'absolute',
              top: 'calc(100% + 4px)',
              left: 0,
              right: 0,
              background: '#0d131f',
              border: '1px solid var(--panel-border)',
              borderRadius: '8px',
              boxShadow: '0 8px 24px rgba(0,0,0,0.7)',
              zIndex: 50,
              overflow: 'hidden'
            }}>
              {searchResults.map(entity => (
                <div
                  key={entity.entity_id}
                  onClick={() => handleSelectSearchResult(entity)}
                  style={{
                    padding: '8px 12px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    borderBottom: '1px solid rgba(255,255,255,0.04)',
                    transition: 'background 0.15s'
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(6,182,212,0.1)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--text-main)' }}>
                    {entity.name}
                  </span>
                  <span style={{ fontSize: '11px', color: 'var(--neon-purple)', textTransform: 'uppercase' }}>
                    {entity.kind}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <button type="submit" className="primary" disabled={loading || !query.trim()}>
          {loading ? 'Analyzing...' : 'Ask AI'}
        </button>
      </form>
      
      {error && (
        <div style={{ color: 'var(--neon-rose)', marginTop: '8px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>⚠️</span> {error}
        </div>
      )}
      
      {resultMsg && (
        <div style={{ marginTop: '12px', padding: '12px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--panel-border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ color: 'var(--neon-emerald)', fontSize: '11px', fontWeight: '700', letterSpacing: '0.5px' }}>
              INTENT: {resultMsg.intent}
            </span>
          </div>
          <div style={{ fontSize: '13.5px', lineHeight: '1.5', color: 'var(--text-main)' }}>
            {resultMsg.explanation}
          </div>
        </div>
      )}
    </div>
  );
}
