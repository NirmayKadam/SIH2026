// Typed client for REST backend
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function getEntityNeighbors(entityId, depth = 1) {
  const res = await fetch(`${BASE_URL}/api/graph/entities/${entityId}/neighbors?depth=${depth}`);
  if (!res.ok) throw new Error(`Failed to fetch neighbors: ${res.status}`);
  return res.json();
}

export async function getEntityDetail(entityId) {
  const res = await fetch(`${BASE_URL}/api/graph/entities/${entityId}`);
  if (!res.ok) throw new Error(`Failed to fetch entity: ${res.status}`);
  return res.json();
}

export async function searchEntities(q = "", limit = 20) {
  const res = await fetch(`${BASE_URL}/api/graph/entities?q=${encodeURIComponent(q)}&limit=${limit}`);
  if (!res.ok) throw new Error(`Failed to search entities: ${res.status}`);
  return res.json();
}

export async function getGraphStats() {
  const res = await fetch(`${BASE_URL}/api/graph/stats`);
  if (!res.ok) throw new Error(`Failed to fetch stats: ${res.status}`);
  return res.json();
}

export async function getCentrality(type = "degree") {
  const res = await fetch(`${BASE_URL}/api/analytics/centrality?type=${type}`);
  if (!res.ok) throw new Error(`Failed to fetch centrality: ${res.status}`);
  return res.json();
}

export async function getCommunities() {
  const res = await fetch(`${BASE_URL}/api/analytics/communities`);
  if (!res.ok) throw new Error(`Failed to fetch communities: ${res.status}`);
  return res.json();
}

export async function askQuestion(question) {
  const res = await fetch(`${BASE_URL}/api/query/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`Query failed: ${res.status}`);
  return res.json();
}

export async function ingestDocument(sourceType, sourcePath) {
  const res = await fetch(`${BASE_URL}/api/ingestion/documents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_type: sourceType, source_path: sourcePath }),
  });
  if (!res.ok) throw new Error(`Ingestion failed: ${res.status}`);
  return res.json();
}

export async function getSuspiciousPatterns() {
  const res = await fetch(`${BASE_URL}/api/analytics/suspicious-patterns`);
  if (!res.ok) throw new Error(`Failed to fetch suspicious patterns: ${res.status}`);
  return res.json();
}
