const BASE_URL = ''

function loadSender() {
  const stored = localStorage.getItem('sender_id')
  if (stored) return stored
  const generated = 'u_' + Math.random().toString(36).slice(2, 10)
  localStorage.setItem('sender_id', generated)
  return generated
}

export function getSenderId() {
  return loadSender()
}

export function getCurrentSessionId() {
  return localStorage.getItem('session_id') || null
}

export function setCurrentSessionId(sessionId) {
  if (sessionId) localStorage.setItem('session_id', sessionId)
  else localStorage.removeItem('session_id')
}

async function request(url, options = {}) {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`)
  }
  return res.status === 204 ? null : res.json()
}

export async function sendChat(text, sessionId) {
  const data = await request('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      sender_id: loadSender(),
      session_id: sessionId || getCurrentSessionId(),
      text,
    }),
  })
  if (data.session_id) setCurrentSessionId(data.session_id)
  return data
}

export async function listSessions() {
  const data = await request(`/api/sessions?sender_id=${encodeURIComponent(loadSender())}`)
  return data.sessions || []
}

export async function createSession(title) {
  return request('/api/sessions', {
    method: 'POST',
    body: JSON.stringify({ sender_id: loadSender(), title: title || null }),
  })
}

export async function renameSession(sessionId, title) {
  return request(`/api/sessions/${encodeURIComponent(sessionId)}`, {
    method: 'PATCH',
    body: JSON.stringify({ sender_id: loadSender(), title }),
  })
}

export async function deleteSession(sessionId) {
  return request(
    `/api/sessions/${encodeURIComponent(sessionId)}?sender_id=${encodeURIComponent(loadSender())}`,
    { method: 'DELETE' },
  )
}

export async function getSessionHistory(sessionId) {
  return request(
    `/api/sessions/${encodeURIComponent(sessionId)}/messages?sender_id=${encodeURIComponent(loadSender())}`,
  )
}
