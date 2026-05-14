// frontend/src/api/analyze.js

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

// Build WS URL safely — handle http/https → ws/wss
function getWsBase() {
  if (API_BASE.startsWith("https://")) return API_BASE.replace("https://", "wss://");
  if (API_BASE.startsWith("http://"))  return API_BASE.replace("http://", "ws://");
  // Fallback: hardcode for local dev
  return "ws://localhost:8000";
}

const WS_BASE = getWsBase();

console.log("[VentureLens] API_BASE:", API_BASE);
console.log("[VentureLens] WS_BASE:", WS_BASE);

export function makeSessionId() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

export function openProgressSocket(sessionId) {
  const url = `${WS_BASE}/ws/${sessionId}`;
  console.log("[VentureLens] Opening WebSocket:", url);
  return new WebSocket(url);
}

export async function analyzeStartup(formData, sessionId) {
  const url = `${API_BASE}/analyze`;
  console.log("[VentureLens] POST", url, { ...formData, session_id: sessionId });

  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...formData, session_id: sessionId }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}