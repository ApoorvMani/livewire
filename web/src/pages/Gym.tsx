import { useState } from 'react'
import { api } from '../api'

const stats = [
  { id: 'strength', label: 'Strength', desc: 'Damage dealt' },
  { id: 'speed', label: 'Speed', desc: 'Hit first, flee' },
  { id: 'defense', label: 'Defense', desc: 'Damage taken' },
  { id: 'dexterity', label: 'Dexterity', desc: 'Dodge & crit' },
]

export default function Gym() {
  const [message, setMessage] = useState('')
  const [training, setTraining] = useState<string | null>(null)

  async function handleTrain(stat: string) {
    setMessage('')
    setTraining(stat)
    try {
      const result = await api.train(stat)
      setMessage(`${stat} +${result.gain} (now ${result.new_value})`)
    } catch (err: any) {
      setMessage(err.message)
    } finally {
      setTraining(null)
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-xl font-bold">Gym</h2>
      <p className="text-sm text-gray-400">5 energy per session</p>
      {message && <p className="bg-gray-800 p-2 rounded text-sm">{message}</p>}
      {stats.map(s => (
        <div key={s.id} className="bg-gray-800 rounded-lg p-3 flex justify-between items-center">
          <div>
            <p className="font-semibold">{s.label}</p>
            <p className="text-xs text-gray-400">{s.desc}</p>
          </div>
          <button className="bg-green-600 px-3 py-2 rounded text-sm min-h-[44px]" onClick={() => handleTrain(s.id)} disabled={training !== null}>
            {training === s.id ? '...' : 'Train'}
          </button>
        </div>
      ))}
    </div>
  )
}
