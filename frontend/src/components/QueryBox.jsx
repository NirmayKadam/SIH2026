import React, { useState } from 'react';
import { askQuestion } from '../api/client';

export default function QueryBox({ onQuerySuccess }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resultMsg, setResultMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResultMsg(null);
    
    try {
      const response = await askQuestion(query);
      setResultMsg({ intent: response.intent, explanation: response.explanation });
      onQuerySuccess(response.result, response.intent, response.explanation);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel animate-slide-down" style={{ padding: '15px' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px' }}>
        <input 
          type="text" 
          placeholder="Ask a question (e.g. 'who is connected to Ravi within 2 hops?')" 
          value={query}
          onChange={e => setQuery(e.target.value)}
          disabled={loading}
          style={{ flexGrow: 1 }}
        />
        <button type="submit" className="primary" disabled={loading || !query.trim()}>
          {loading ? 'Analyzing...' : 'Query'}
        </button>
      </form>
      
      {error && <div style={{ color: '#ef4444', marginTop: '10px', fontSize: '14px' }}>Error: {error}</div>}
      
      {resultMsg && (
        <div style={{ marginTop: '15px', padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
          <div style={{ color: 'var(--neon-emerald)', fontSize: '12px', fontWeight: 'bold', marginBottom: '5px' }}>
            INTENT CLASSIFIED: {resultMsg.intent}
          </div>
          <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
            {resultMsg.explanation}
          </div>
        </div>
      )}
    </div>
  );
}
