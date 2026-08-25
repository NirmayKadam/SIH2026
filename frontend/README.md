# Frontend

Not yet scaffolded beyond the API client (`src/api/client.js`), which maps 1:1 to
the real backend endpoints in ARCHITECTURE.md. Recommended: React + vis-network
for the graph view (already in package.json), a search bar, and the NL query box
hitting `askQuestion()`.

Every function in `src/api/client.js` hits a real endpoint — don't add fallback
mock data if a call fails; surface the real error instead (see the root
ARCHITECTURE.md hard rules — this applies to frontend too).
