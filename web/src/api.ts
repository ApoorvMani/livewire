const BASE = '/api'

async function request(path: string, options?: RequestInit) {
  const res = await fetch(BASE + path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (res.status === 401) {
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    const body = await res.json()
    throw new Error(body.detail?.error || body.error || res.statusText)
  }
  return res.json()
}

export const auth = {
  register: (username: string, password: string) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify({ username, password }) }),
  login: (username: string, password: string) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  logout: () => request('/auth/logout', { method: 'POST' }),
}

export const api = {
  me: () => request('/me'),
  crimes: () => request('/crimes'),
  attemptCrime: (id: string) => request(`/crimes/${id}/attempt`, { method: 'POST' }),
  train: (stat: string) => request(`/gym/train/${stat}`, { method: 'POST' }),
  listJail: () => request('/jail/list'),
  bust: (charId: number) => request(`/jail/${charId}/bust`, { method: 'POST' }),
}
