// Typed-ish client for the REST boundary defined in ARCHITECTURE.md.
// Every function here maps 1:1 to a real backend endpoint — no mock data,
// no placeholder responses. If the backend isn't ready yet, let the fetch fail
// and show a real error state in the UI, don't fake a response here.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function getEntityNeighbors(entityId, depth = 1) {
  const res = await fetch(`${BASE_URL}/api/graph/entities/${entityId}/neighbors?depth=${depth}`);
  if (!res.ok) throw new Error(`Failed to fetch neighbors: ${res.status}`);
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
