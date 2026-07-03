interface Props {
  energy: number; maxEnergy: number
  nerve: number; maxNerve: number
  health: number; maxHealth: number
}

export default function Bars({ energy, maxEnergy, nerve, maxNerve, health, maxHealth }: Props) {
  return (
    <div className="flex flex-col gap-2">
      <BarRow label="Energy" value={energy} max={maxEnergy} color="bg-yellow-500" />
      <BarRow label="Nerve" value={nerve} max={maxNerve} color="bg-purple-500" />
      <BarRow label="Health" value={health} max={maxHealth} color="bg-green-500" />
    </div>
  )
}

function BarRow({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span>{label}</span>
        <span>{value}/{max}</span>
      </div>
      <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
