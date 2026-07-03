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
  attack: (targetName: string, choice: string) =>
    request('/attack', { method: 'POST', body: JSON.stringify({ target_name: targetName, choice }) }),
  deposit: (amount: number) => request('/bank/deposit', { method: 'POST', body: JSON.stringify({ amount }) }),
  withdraw: (amount: number) => request('/bank/withdraw', { method: 'POST', body: JSON.stringify({ amount }) }),
  shop: () => request('/shop'),
  buyItem: (itemId: number, qty: number) =>
    request('/shop/buy', { method: 'POST', body: JSON.stringify({ item_id: itemId, qty }) }),
  inventory: () => request('/inventory'),
  equip: (id: number) => request(`/inventory/${id}/equip`, { method: 'POST' }),
  unequip: (id: number) => request(`/inventory/${id}/unequip`, { method: 'POST' }),
  useItem: (id: number) => request(`/inventory/${id}/use`, { method: 'POST' }),
}
