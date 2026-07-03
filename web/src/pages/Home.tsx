import { useState } from 'react'
import Bars from '../components/Bars'
import HeatGauge from '../components/HeatGauge'
import ActivityFeed from '../components/ActivityFeed'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

interface Props { user: any }

export default function Home({ user }: Props) {
  const navigate = useNavigate()
  const [depositAmt, setDepositAmt] = useState('')
  const [withdrawAmt, setWithdrawAmt] = useState('')
  const [bankMsg, setBankMsg] = useState('')
  const [cash, setCash] = useState(user.cash)
  const [bank, setBank] = useState(user.bank || 0)
  const [heat, setHeat] = useState(user.heat)
  const [collectMsg, setCollectMsg] = useState('')
  const [canCollect, setCanCollect] = useState(user.can_collect)

  async function deposit() {
    const amt = parseInt(depositAmt)
    if (!amt || amt <= 0) return
    try {
      const res = await api.deposit(amt)
      setCash(res.cash)
      setBank(res.bank)
      setBankMsg(`Deposited $${amt} (fee $${res.fee})`)
    } catch (err: any) { setBankMsg(err.message) }
  }

  async function withdraw() {
    const amt = parseInt(withdrawAmt)
    if (!amt || amt <= 0) return
    try {
      const res = await api.withdraw(amt)
      setCash(res.cash)
      setBank(res.bank)
      setBankMsg(`Withdrew $${amt}`)
    } catch (err: any) { setBankMsg(err.message) }
  }

  async function handleCollect() {
    try {
      const res = await api.collectJob()
      setCash(res.cash)
      setCanCollect(false)
      setCollectMsg(`Collected $${res.pay} from ${res.job_name}`)
      setTimeout(() => setCollectMsg(''), 3000)
    } catch (err: any) { setCollectMsg(err.message) }
  }

  function handleHeatUpdate(data: any) {
    setHeat(data.heat)
    setCash(data.cash)
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-xl font-bold mb-1">{user.name}</h2>
        <p className="text-sm text-gray-400">Level {user.level} · ${cash}</p>
      </div>
      <div className="bg-gray-800 rounded-lg p-4">
        <Bars
          energy={user.energy} maxEnergy={user.max_energy}
          nerve={user.nerve} maxNerve={user.max_nerve}
          health={user.health} maxHealth={user.max_health}
        />
      </div>
      <div className="bg-gray-800 rounded-lg p-4">
        <HeatGauge heat={heat} onUpdate={handleHeatUpdate} />
      </div>
      {user.job_name && (
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="font-semibold mb-1">{user.job_name}</h3>
          <p className="text-sm text-gray-400">Pay: ${user.job_pay}/day</p>
          {collectMsg && <p className="text-xs text-gray-400 mb-2">{collectMsg}</p>}
          {canCollect ? (
            <button className="bg-blue-600 px-3 py-1 rounded text-sm mt-2" onClick={handleCollect}>
              Collect
            </button>
          ) : (
            <p className="text-xs text-gray-500 mt-2">Collected today — come back tomorrow</p>
          )}
        </div>
      )}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="font-semibold mb-2">Bank — ${bank}</h3>
        {bankMsg && <p className="text-xs text-gray-400 mb-2">{bankMsg}</p>}
        <div className="flex gap-2">
          <input className="bg-gray-700 rounded p-2 text-sm w-24" placeholder="Amount" value={depositAmt} onChange={e => setDepositAmt(e.target.value)} />
          <button className="bg-blue-600 px-3 py-1 rounded text-sm" onClick={deposit}>Deposit</button>
        </div>
        <div className="flex gap-2 mt-2">
          <input className="bg-gray-700 rounded p-2 text-sm w-24" placeholder="Amount" value={withdrawAmt} onChange={e => setWithdrawAmt(e.target.value)} />
          <button className="bg-green-600 px-3 py-1 rounded text-sm" onClick={withdraw}>Withdraw</button>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <button className="bg-gray-800 p-4 rounded-lg text-left" onClick={() => navigate('/crimes')}>
          <div className="text-2xl mb-1">💀</div>
          <div className="font-semibold">Crimes</div>
          <div className="text-xs text-gray-400">Spend nerve for cash</div>
        </button>
        <button className="bg-gray-800 p-4 rounded-lg text-left" onClick={() => navigate('/gym')}>
          <div className="text-2xl mb-1">🏋️</div>
          <div className="font-semibold">Gym</div>
          <div className="text-xs text-gray-400">Train your stats</div>
        </button>
      </div>
      <ActivityFeed />
    </div>
  )
}
