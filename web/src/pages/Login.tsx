import { useState } from 'react'
import { auth } from '../api'

interface Props { onLogin: () => void }

export default function Login({ onLogin }: Props) {
  const [tab, setTab] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      if (tab === 'register') await auth.register(username, password)
      else await auth.login(username, password)
      onLogin()
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-3xl font-bold mb-8">LIVEWIRE</h1>
      <div className="flex mb-4">
        <button className={`px-4 py-2 ${tab === 'login' ? 'bg-blue-600' : 'bg-gray-700'}`} onClick={() => setTab('login')}>Login</button>
        <button className={`px-4 py-2 ${tab === 'register' ? 'bg-blue-600' : 'bg-gray-700'}`} onClick={() => setTab('register')}>Register</button>
      </div>
      <form onSubmit={handleSubmit} className="w-full max-w-xs flex flex-col gap-3">
        <input className="bg-gray-800 p-3 rounded" name="username" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
        <input className="bg-gray-800 p-3 rounded" name="password" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button className="bg-blue-600 p-3 rounded font-semibold" type="submit">
          {tab === 'login' ? 'Login' : 'Register'}
        </button>
      </form>
    </div>
  )
}
