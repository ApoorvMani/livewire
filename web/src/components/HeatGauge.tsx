import { api } from '../api'

interface Props {
  heat: number
  onUpdate: (data: any) => void
}

export default function HeatGauge({ heat, onUpdate }: Props) {
  const color = heat < 40 ? 'bg-green-500' : heat < 70 ? 'bg-yellow-500' : 'bg-red-500'
  const label = heat < 40 ? 'Low' : heat < 70 ? 'Wanted' : 'Hot'

  async function handleBribe() {
    try {
      const res = await api.bribe()
      onUpdate(res)
    } catch (err: any) {
      alert(err.message)
    }
  }

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span>Heat</span>
        <span>{heat}/100 · {label}</span>
      </div>
      <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-500`} style={{ width: `${heat}%` }} />
      </div>
      {heat >= 40 && (
        <button className="mt-2 bg-orange-600 px-3 py-1 rounded text-sm w-full" onClick={handleBribe}>
          Bribe (${heat * 100})
        </button>
      )}
    </div>
  )
}
