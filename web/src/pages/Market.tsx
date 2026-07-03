import { useState, useEffect } from 'react'
import { api } from '../api'

export default function Market() {
  const [tab, setTab] = useState<'shop' | 'inventory' | 'bazaar'>('shop')
  const [shopItems, setShopItems] = useState<any[]>([])
  const [inventory, setInventory] = useState<any[]>([])
  const [msg, setMsg] = useState('')
  const [cash, setCash] = useState<number | null>(null)

  useEffect(() => { loadShop() }, [])
  useEffect(() => { if (tab === 'inventory') loadInventory() }, [tab])
  useEffect(() => { if (tab === 'bazaar') { loadInventory(); loadMyListings(); loadOrderBook() } }, [tab])

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

  async function buyItem(itemId: number) {
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

  const [bazaarItemId, setBazaarItemId] = useState<number>(0)
  const [listPrice, setListPrice] = useState('')
  const [listQty, setListQty] = useState('1')
  const [orderBook, setOrderBook] = useState<any[]>([])
  const [myListings, setMyListings] = useState<any[]>([])
  const [selectedItemId, setSelectedItemId] = useState<number>(0)

  async function loadOrderBook() {
    if (!selectedItemId) return
    try {
      const listings = await api.marketOrderBook(selectedItemId)
      setOrderBook(listings)
    } catch (err: any) { setMsg(err.message) }
  }

  async function loadMyListings() {
    try {
      const data = await api.marketMyListings()
      setMyListings(data)
    } catch (err: any) { setMsg(err.message) }
  }

  async function handleList(e: React.FormEvent) {
    e.preventDefault()
    setMsg('')
    const price = parseInt(listPrice)
    const qty = parseInt(listQty)
    if (!bazaarItemId || isNaN(price) || isNaN(qty) || qty < 1 || price < 1) {
      setMsg('Invalid input')
      return
    }
    try {
      const res = await api.marketList(bazaarItemId, price, qty)
      setMsg(`Listed! Fee: $${res.fee}`)
      loadInventory()
      loadOrderBook()
      loadMyListings()
      setListPrice('')
      setListQty('1')
    } catch (err: any) { setMsg(err.message) }
  }

  async function handleBuy(listingId: number, qty: number) {
    setMsg('')
    try {
      const res = await api.marketBuy(listingId, qty)
      setCash(res.total)
      setMsg(`Bought ${res.qty} items for $${res.total}`)
      loadOrderBook()
      loadMyListings()
      loadInventory()
    } catch (err: any) { setMsg(err.message) }
  }

  async function handleCancel(listingId: number) {
    setMsg('')
    try {
      await api.marketCancel(listingId)
      setMsg('Listing cancelled')
      loadMyListings()
      loadOrderBook()
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
        <button
          className={`flex-1 p-2 rounded-t text-sm ${tab === 'bazaar' ? 'bg-blue-600' : 'bg-gray-800'}`}
          onClick={() => setTab('bazaar')}
        >
          Bazaar
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
              <button className="bg-green-600 px-3 py-2 rounded text-sm" onClick={() => buyItem(item.id)}>
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

      {tab === 'bazaar' && (
        <div className="flex flex-col gap-4">
          <div className="bg-gray-800 rounded-lg p-3">
            <h3 className="font-semibold mb-2">List an Item</h3>
            <form onSubmit={handleList} className="flex flex-col gap-2">
              <select
                className="bg-gray-700 rounded p-2 text-sm"
                value={bazaarItemId}
                onChange={e => setBazaarItemId(Number(e.target.value))}
              >
                <option value={0}>Select item...</option>
                {inventory.map((inv: any) => (
                  <option key={inv.id} value={inv.item_id}>{inv.name} (x{inv.qty})</option>
                ))}
              </select>
              <div className="flex gap-2">
                <input
                  type="number"
                  placeholder="Price per item"
                  className="bg-gray-700 rounded p-2 text-sm flex-1"
                  value={listPrice}
                  onChange={e => setListPrice(e.target.value)}
                  min={1}
                />
                <input
                  type="number"
                  placeholder="Qty"
                  className="bg-gray-700 rounded p-2 text-sm w-20"
                  value={listQty}
                  onChange={e => setListQty(e.target.value)}
                  min={1}
                />
              </div>
              <button type="submit" className="bg-green-600 p-2 rounded text-sm">List for Sale</button>
            </form>
          </div>

          <div className="bg-gray-800 rounded-lg p-3">
            <h3 className="font-semibold mb-2">Order Book</h3>
            <div className="flex gap-2 mb-2">
              <select
                className="bg-gray-700 rounded p-2 text-sm flex-1"
                value={selectedItemId}
                onChange={e => { setSelectedItemId(Number(e.target.value)); setBazaarItemId(Number(e.target.value)) }}
              >
                <option value={0}>Select item...</option>
                {shopItems.map((item: any) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
              <button className="bg-blue-600 px-3 py-1 rounded text-sm" onClick={loadOrderBook}>Refresh</button>
            </div>
            {orderBook.length === 0 && <p className="text-gray-400 text-sm">No listings</p>}
            {orderBook.map((l: any) => (
              <div key={l.id} className="flex justify-between items-center bg-gray-700 rounded p-2 mb-1 text-sm">
                <span>${l.price} x{l.qty}</span>
                <button className="bg-green-600 px-2 py-1 rounded text-xs" onClick={() => handleBuy(l.id, 1)}>
                  Buy 1
                </button>
              </div>
            ))}
          </div>

          <div className="bg-gray-800 rounded-lg p-3">
            <h3 className="font-semibold mb-2">My Listings</h3>
            {myListings.length === 0 && <p className="text-gray-400 text-sm">No active listings</p>}
            {myListings.map((l: any) => (
              <div key={l.id} className="flex justify-between items-center bg-gray-700 rounded p-2 mb-1 text-sm">
                <span>Item {l.item_id} — ${l.price} x{l.qty}</span>
                <button className="bg-red-600 px-2 py-1 rounded text-xs" onClick={() => handleCancel(l.id)}>
                  Cancel
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
