const loc = window.location;
const API_BASE = `${loc.protocol}//${loc.hostname}:8000`;
let _sessionId = null;

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
    if (data.session_id) _sessionId = data.session_id;
    return data;
  },

  async verifyAnswer(gameType, answer) {
    const res = await fetch(`${API_BASE}/api/verify`, {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ game_type: gameType, answer }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
};
