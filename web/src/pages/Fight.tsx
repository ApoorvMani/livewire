import { useState } from 'react'
import { api } from '../api'

export default function Fight() {
  const [target, setTarget] = useState('')
  const [choice, setChoice] = useState('mug')
  const [result, setResult] = useState<any>(null)
  const [msg, setMsg] = useState('')
  const [attacking, setAttacking] = useState(false)

  async function attack() {
    setMsg(''); setResult(null)
    if (!target) { setMsg('Enter a target name'); return }
    setAttacking(true)
    try {
      const res = await api.attack(target, choice)
      setResult(res)
    } catch (err: any) { setMsg(err.message) }
    finally { setAttacking(false) }
  }

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-xl font-bold">Fight</h2>
      {msg && <p className="bg-gray-800 p-2 rounded text-sm">{msg}</p>}
      <input className="bg-gray-800 rounded-lg p-3 text-sm w-full min-h-[44px]" placeholder="Target name" value={target} onChange={e => setTarget(e.target.value)} />
      <div className="flex gap-2">
        {['mug', 'hospitalize', 'leave'].map(c => (
          <button key={c} className={`flex-1 p-2 rounded text-sm min-h-[44px] ${choice === c ? 'bg-blue-600' : 'bg-gray-700'}`} onClick={() => setChoice(c)}>{c}</button>
        ))}
      </div>
      <button className="bg-red-600 p-3 rounded-lg font-semibold min-h-[44px]" onClick={attack} disabled={attacking}>
        {attacking ? 'Attacking...' : 'Attack (25 energy)'}
      </button>
      {result && (
        <div className="bg-gray-800 rounded-lg p-3">
          <p className={result.won ? 'text-green-400' : 'text-red-400'}>{result.won ? 'Won!' : 'Lost!'}</p>
          {result.mug_amount > 0 && <p className="text-sm">Stole ${result.mug_amount}</p>}
          <p className="text-xs text-gray-400">XP +{result.xp}</p>
        </div>
      )}
    </div>
  )
}
