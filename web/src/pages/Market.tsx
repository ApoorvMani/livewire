import { useState, useEffect } from 'react'
import { api } from '../api'

export default function Market() {
  const [tab, setTab] = useState<'shop' | 'inventory'>('shop')
  const [shopItems, setShopItems] = useState<any[]>([])
  const [inventory, setInventory] = useState<any[]>([])
  const [msg, setMsg] = useState('')
  const [cash, setCash] = useState<number | null>(null)

  useEffect(() => { loadShop() }, [])
  useEffect(() => { if (tab === 'inventory') loadInventory() }, [tab])

  async function loadShop() {
    try {
      const items = await api.shop()
      setShopItems(items)
    } catch (err: any) { setMsg(err.message) }
  }

  async function loadInventory() {
    try {
      const inv = await api.inventory()
      setInventory(inv)
    } catch (err: any) { setMsg(err.message) }
  }

  async function buy(itemId: number) {
    setMsg('')
    try {
      const res = await api.buyItem(itemId, 1)
      setCash(res.cash)
    } catch (err: any) { setMsg(err.message) }
  }

  async function equip(id: number) {
    setMsg('')
    try {
      await api.equip(id)
      loadInventory()
    } catch (err: any) { setMsg(err.message) }
  }

  async function unequip(id: number) {
    setMsg('')
    try {
      await api.unequip(id)
      loadInventory()
    } catch (err: any) { setMsg(err.message) }
  }

  async function useItem(id: number) {
    setMsg('')
    try {
      await api.useItem(id)
      loadInventory()
    } catch (err: any) { setMsg(err.message) }
  }

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-xl font-bold">Market</h2>
      {cash !== null && <p className="text-sm text-green-400">Cash: ${cash}</p>}
      {msg && <p className="bg-gray-800 p-2 rounded text-sm">{msg}</p>}
      <div className="flex gap-2 border-b border-gray-700 pb-2">
        <button
          className={`flex-1 p-2 rounded-t text-sm ${tab === 'shop' ? 'bg-blue-600' : 'bg-gray-800'}`}
          onClick={() => setTab('shop')}
        >
          Shop
        </button>
        <button
          className={`flex-1 p-2 rounded-t text-sm ${tab === 'inventory' ? 'bg-blue-600' : 'bg-gray-800'}`}
          onClick={() => setTab('inventory')}
        >
          Inventory
        </button>
      </div>

      {tab === 'shop' && (
        <div className="flex flex-col gap-2">
          {shopItems.map(item => (
            <div key={item.id} className="bg-gray-800 rounded-lg p-3 flex justify-between items-center">
              <div>
                <p className="font-semibold">{item.name}</p>
                <p className="text-xs text-gray-400">
                  {item.slot === 'consumable' ? 'Consumable' : `${item.slot} +${item.bonus}`}
                  {' · '}${item.base_price}
                  {item.daily_cap ? ` · cap: ${item.daily_cap}/day` : ''}
                </p>
              </div>
              <button className="bg-green-600 px-3 py-2 rounded text-sm" onClick={() => buy(item.id)}>
                Buy
              </button>
            </div>
          ))}
        </div>
      )}

      {tab === 'inventory' && (
        <div className="flex flex-col gap-2">
          {inventory.length === 0 && <p className="text-gray-400 text-sm">No items</p>}
          {inventory.map((item: any) => (
            <div key={item.id} className="bg-gray-800 rounded-lg p-3 flex justify-between items-center">
              <div>
                <p className="font-semibold">
                  {item.name}
                  {item.equipped && <span className="text-green-400 text-xs ml-2">equipped</span>}
                </p>
                <p className="text-xs text-gray-400">
                  {item.slot === 'consumable' ? 'Consumable' : `${item.slot} +${item.bonus}`}
                  {' · '}x{item.qty}
                </p>
              </div>
              <div className="flex gap-1">
                {item.slot === 'consumable' ? (
                  <button className="bg-blue-600 px-2 py-1 rounded text-xs" onClick={() => useItem(item.id)}>
                    Use
                  </button>
                ) : item.equipped ? (
                  <button className="bg-yellow-600 px-2 py-1 rounded text-xs" onClick={() => unequip(item.id)}>
                    Unequip
                  </button>
                ) : (
                  <button className="bg-purple-600 px-2 py-1 rounded text-xs" onClick={() => equip(item.id)}>
                    Equip
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
