import { useState, useEffect } from 'react'
import './App.css'
import { API } from './api'
import HomePage from './pages/HomePage'
import HowItWorksPage from './pages/HowItWorksPage'
import AboutPage from './pages/AboutPage'
import ChatPage from './pages/ChatPage'

export default function App() {
  const [page, setPage] = useState('home')
  const [userId] = useState(() => {
    let id = localStorage.getItem('aivestia_user_id')
    if (!id) {
      id = crypto.randomUUID()
      localStorage.setItem('aivestia_user_id', id)
    }
    return id
  })

  useEffect(() => {
    fetch(`${API}/users?user_id=${userId}`, { method: 'POST' }).catch(() => {})
  }, [userId])

  return (
    <div className="app">
      <header className="header">
        <div className="logo" onClick={() => setPage('home')} style={{ cursor: 'pointer' }}>
          <span className="logo-icon">◈</span>
          <span className="logo-text">Aivestia</span>
        </div>
        <nav className="nav">
          <a href="#" className={page === 'how-it-works' ? 'nav-active' : ''} onClick={e => { e.preventDefault(); setPage('how-it-works') }}>How it works</a>
          <a href="#" className={page === 'about' ? 'nav-active' : ''} onClick={e => { e.preventDefault(); setPage('about') }}>About</a>
          <button className="btn-primary" onClick={() => setPage('chat')}>Get Started</button>
        </nav>
      </header>

      {page === 'home'         && <HomePage onNavigate={setPage} />}
      {page === 'how-it-works' && <HowItWorksPage />}
      {page === 'about'        && <AboutPage />}
      {page === 'chat'         && <ChatPage onBack={() => setPage('home')} userId={userId} />}
    </div>
  )
}
