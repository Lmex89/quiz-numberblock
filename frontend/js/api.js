const loc = window.location;
const API_BASE = `${loc.protocol}//${loc.hostname}:8000`;
const SESSION_STORAGE_KEY = 'quiz_session_cache_v1';
const SESSION_TTL_MS = 10 * 60 * 1000;

function readStoredSessionId() {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || !parsed.sessionId || typeof parsed.expiresAt !== 'number') {
      localStorage.removeItem(SESSION_STORAGE_KEY);
      return null;
    }
    if (Date.now() > parsed.expiresAt) {
      localStorage.removeItem(SESSION_STORAGE_KEY);
      return null;
    }
    return parsed.sessionId;
  } catch {
    return null;
  }
}

function persistSessionId(sessionId) {
  try {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({
      sessionId,
      expiresAt: Date.now() + SESSION_TTL_MS,
    }));
  } catch {
    // no-op when storage is unavailable
  }
}

let _sessionId = readStoredSessionId();

function headers() {
  const h = { 'Content-Type': 'application/json' };
  if (_sessionId) h['X-Session-Id'] = _sessionId;
  return h;
}

const API = {
  async getQuiz(gameType) {
    const res = await fetch(`${API_BASE}/api/quiz/${gameType}`, { headers: headers() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.session_id) {
      _sessionId = data.session_id;
      persistSessionId(_sessionId);
    }
    return data;
  },

  async verifyAnswer(gameType, answer) {
    const res = await fetch(`${API_BASE}/api/verify`, {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ game_type: gameType, answer }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.session_id) {
      _sessionId = data.session_id;
      persistSessionId(_sessionId);
    }
    return data;
  },
};
