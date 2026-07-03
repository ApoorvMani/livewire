import { useState, useEffect } from 'react'
import { api } from '../api'

const EVENT_ICONS: Record<string, string> = {
  crime: '💀', train: '🏋️', attack: '⚔️', bust: '🔓',
  trade: '💰', job_pay: '💼', use_item: '📦', bribe: '💵',
  levelup: '⬆️', shakedown: '🚔', raid: '👮',
}

export default function ActivityFeed() {
  const [events, setEvents] = useState<any[]>([])

  useEffect(() => {
    api.feed().then(setEvents).catch(() => {})
    const interval = setInterval(() => { api.feed().then(setEvents).catch(() => {}) }, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="bg-gray-800 rounded-lg p-3">
      <h3 className="text-sm font-semibold mb-2 text-gray-300">Recent Activity</h3>
      {events.length === 0 && <p className="text-xs text-gray-500">No recent activity.</p>}
      {events.map((e: any) => (
        <div key={e.id} className="flex items-center gap-2 py-1 text-sm">
          <span>{EVENT_ICONS[e.type] || '📌'}</span>
          <span className="text-gray-300">{e.type}</span>
          <span className="text-xs text-gray-500 ml-auto">{e.mins_ago}m ago</span>
        </div>
      ))}
    </div>
  )
}
