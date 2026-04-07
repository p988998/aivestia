import { useState, useEffect, useCallback } from 'react'
import './App.css'
import { API } from './api'
import HomePage from './pages/HomePage'
import HowItWorksPage from './pages/HowItWorksPage'
import AboutPage from './pages/AboutPage'
import ChatPage from './pages/ChatPage'

export default function App() {
  const [page, setPage] = useState(() => {
    const p = window.history.state?.page
    return p || 'home'
  })
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

  useEffect(() => {
    const onPopState = (e) => {
      setPage(e.state?.page || 'home')
    }
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  const navigate = useCallback((newPage) => {
    window.history.pushState({ page: newPage }, '', `#${newPage}`)
    setPage(newPage)
  }, [])

  return (
    <div className="app">
      <header className="header">
        <div className="logo" onClick={() => navigate('home')} style={{ cursor: 'pointer' }}>
          <span className="logo-icon">◈</span>
          <span className="logo-text">Aivestia</span>
        </div>
        <nav className="nav">
          <a href="#" className={page === 'how-it-works' ? 'nav-active' : ''} onClick={e => { e.preventDefault(); navigate('how-it-works') }}>How it works</a>
          <a href="#" className={page === 'about' ? 'nav-active' : ''} onClick={e => { e.preventDefault(); navigate('about') }}>About</a>
        </nav>
      </header>

      {page === 'home'         && <HomePage onNavigate={navigate} />}
      {page === 'how-it-works' && <HowItWorksPage />}
      {page === 'about'        && <AboutPage />}
      {page === 'chat'         && <ChatPage onBack={() => navigate('home')} userId={userId} />}
    </div>
  )
}
