import { useState, useEffect } from 'react'
import { api } from '../api'

export default function Crimes() {
  const [crimes, setCrimes] = useState<any[]>([])
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState<string | null>(null)

  useEffect(() => {
    api.crimes().then(setCrimes).finally(() => setLoading(false))
  }, [])

  async function attempt(id: string) {
    setMessage('')
    setSubmitting(id)
    try {
      const result = await api.attemptCrime(id)
      setMessage(result.success ? `Got $${result.payout}` : 'Failed!')
      setCrimes(await api.crimes())
    } catch (err: any) {
      setMessage(err.message)
    } finally {
      setSubmitting(null)
    }
  }

  const tiers = [1,2,3,4,5]
  const grouped = tiers.map(t => ({ tier: t, crimes: crimes.filter((c: any) => c.tier === t) }))

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-xl font-bold">Crimes</h2>
      {message && <p className="bg-gray-800 p-2 rounded text-sm">{message}</p>}
      {loading && <p className="text-gray-400 text-sm">Loading crimes...</p>}
      {!loading && crimes.length === 0 && <p className="text-gray-400 text-sm">No crimes available.</p>}
      {grouped.map(g => g.crimes.length > 0 && (
        <div key={g.tier}>
          <h3 className="text-sm text-gray-400 uppercase mb-1">Tier {g.tier}</h3>
          {g.crimes.map((c: any) => (
            <div key={c.id} className="bg-gray-800 rounded-lg p-3 mb-2 flex justify-between items-center">
              <div>
                <p className="font-semibold">{c.name}</p>
                <p className="text-xs text-gray-400">{c.nerve_cost} nerve · {c.payout_min}-{c.payout_max} · {Math.round(c.success_p*100)}%</p>
              </div>
              <button className="bg-blue-600 px-3 py-2 rounded text-sm min-h-[44px]" onClick={() => attempt(c.id)} disabled={submitting !== null}>
                {submitting === c.id ? '...' : 'Go'}
              </button>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
