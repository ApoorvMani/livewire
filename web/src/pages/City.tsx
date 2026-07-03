import { useState, useEffect } from 'react'
import { api } from '../api'

export default function City() {
  const [jailed, setJailed] = useState<any[]>([])
  const [msg, setMsg] = useState('')

  useEffect(() => { api.listJail().then(setJailed).catch(() => {}) }, [])

  async function bust(id: number) {
    setMsg('')
    try {
      const res = await api.bust(id)
      setMsg(res.success ? 'Bust successful!' : 'Bust failed — you got jailed!')
      setJailed(await api.listJail())
    } catch (err: any) { setMsg(err.message) }
  }

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-xl font-bold">City Jail</h2>
      {msg && <p className="bg-gray-800 p-2 rounded text-sm">{msg}</p>}
      {jailed.length === 0 && <p className="text-gray-400 text-sm">No one is jailed right now.</p>}
      {jailed.map((c: any) => (
        <div key={c.id} className="bg-gray-800 rounded-lg p-3 flex justify-between items-center">
          <div>
            <p className="font-semibold">{c.name}</p>
            <p className="text-xs text-gray-400">Lvl {c.level} · {c.minutes_left}m left</p>
          </div>
          <button className="bg-blue-600 px-3 py-2 rounded text-sm" onClick={() => bust(c.id)}>Bust</button>
        </div>
      ))}
    </div>
  )
}
