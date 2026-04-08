import { useState, useRef, useEffect } from 'react'
import { API } from '../api'
import { renderMarkdown } from '../utils/markdown'
import ChatSidebar from '../components/ChatSidebar'
import SuggestionBar from '../components/SuggestionBar'
import PortfolioForm from '../components/PortfolioForm'
import SimulationCard from '../components/SimulationCard'
import SourcesPanel from '../components/SourcesPanel'

const WELCOME_MESSAGE = {
  role: 'assistant',
  content: "Hi! I'm your Aivestia advisor. Ask me anything about investing, ETFs, risk levels, or portfolio strategies.",
  sources: [],
}

export default function ChatPage({ onBack, userId }) {
  const [mode, setMode] = useState('chat')
  const [chats, setChats] = useState([])
  const [activeChatId, setActiveChatId] = useState(null)
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [input, setInput] = useState('')
  const [loadingChatId, setLoadingChatId] = useState(null)
  const [streamingChatId, setStreamingChatId] = useState(null)
  const [statusMessage, setStatusMessage] = useState('')
  const [portfolioContext, setPortfolioContext] = useState(null)
  const [suggestions, setSuggestions] = useState([])
  const [editingChatId, setEditingChatId] = useState(null)
  const [editingTitle, setEditingTitle] = useState('')
  const bottomRef = useRef(null)
  const editInputRef = useRef(null)

  useEffect(() => {
    loadChats()
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loadingChatId])

  async function loadChats() {
    try {
      const res = await fetch(`${API}/users/${userId}/chats`)
      const data = await res.json()
      setChats(data)
      if (data.length > 0) {
        await selectChat(data[0].id)
      } else {
        await createNewChat()
      }
    } catch {
      // backend unavailable, start with local empty state
    }
  }

  async function createNewChat() {
    try {
      const res = await fetch(`${API}/users/${userId}/chats`, { method: 'POST' })
      const chat = await res.json()
      setChats(prev => [chat, ...prev])
      setActiveChatId(chat.id)
      setMessages([WELCOME_MESSAGE])
      setMode('chat')
    } catch {
      const localId = crypto.randomUUID()
      setActiveChatId(localId)
      setMessages([WELCOME_MESSAGE])
    }
  }

  async function fetchSuggestions(lastAssistantMessage) {
    try {
      const res = await fetch(`${API}/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ last_message: lastAssistantMessage }),
      })
      const data = await res.json()
      setSuggestions(data.suggestions || [])
    } catch {
      setSuggestions([])
    }
  }

  async function selectChat(chatId) {
    setActiveChatId(chatId)
    setSuggestions([])
    setMode('chat')
    try {
      const res = await fetch(`${API}/chats/${chatId}/messages`)
      const msgs = await res.json()
      setMessages(msgs.length > 0 ? msgs : [WELCOME_MESSAGE])
    } catch {
      setMessages([WELCOME_MESSAGE])
    }
  }

  function startEditTitle(chat, e) {
    e.stopPropagation()
    setEditingChatId(chat.id)
    setEditingTitle(chat.title || '')
    setTimeout(() => editInputRef.current?.select(), 0)
  }

  async function commitEditTitle(chatId) {
    const title = editingTitle.trim()
    setEditingChatId(null)
    if (!title) return
    setChats(prev => prev.map(c => c.id === chatId ? { ...c, title } : c))
    try {
      await fetch(`${API}/chats/${chatId}/title?title=${encodeURIComponent(title)}`, { method: 'PATCH' })
    } catch {
      // best-effort
    }
  }

  function handleEditKeyDown(e, chatId) {
    if (e.key === 'Enter') { e.preventDefault(); commitEditTitle(chatId) }
    if (e.key === 'Escape') { setEditingChatId(null) }
  }

  async function deleteChat(chatId, e) {
    e.stopPropagation()
    try {
      await fetch(`${API}/chats/${chatId}`, { method: 'DELETE' })
    } catch {
      // best-effort
    }
    const remaining = chats.filter(c => c.id !== chatId)
    setChats(remaining)
    if (activeChatId === chatId) {
      if (remaining.length > 0) {
        await selectChat(remaining[0].id)
      } else {
        await createNewChat()
      }
    }
  }

  async function handleSend(overrideText) {
    const text = (overrideText !== undefined ? overrideText : input).trim()
    const chatId = activeChatId
    if (!text || streamingChatId || loadingChatId || !chatId) return

    setInput('')
    setSuggestions([])
    setMessages(prev => [...prev, { role: 'user', content: text, sources: [] }])
    setLoadingChatId(chatId)
    setStreamingChatId(chatId)
    setStatusMessage('')

    try {
      const res = await fetch(`${API}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, chat_id: chatId, user_id: userId, user_profile: portfolioContext ?? {} }),
      })

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let firstToken = true

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop()

        for (const part of parts) {
          const lines = part.split('\n')
          let eventType = 'message'
          let dataStr = ''
          for (const line of lines) {
            if (line.startsWith('event: ')) eventType = line.slice(7).trim()
            if (line.startsWith('data: '))  dataStr  = line.slice(6).trim()
          }
          if (!dataStr) continue
          const data = JSON.parse(dataStr)

          if (eventType === 'status') {
            setStatusMessage(data.message)
          } else if (eventType === 'retry') {
            setStatusMessage('Refining answer...')
          } else if (eventType === 'token') {
            if (firstToken) {
              setMessages(prev => [...prev, { role: 'assistant', content: '', sources: [] }])
              setLoadingChatId(null)
              setStatusMessage('')
              firstToken = false
            }
            setMessages(prev => {
              const msgs = [...prev]
              const last = msgs[msgs.length - 1]
              return [...msgs.slice(0, -1), { ...last, content: last.content + data }]
            })
          } else if (eventType === 'done') {
            setMessages(prev => {
              const msgs = [...prev]
              const last = msgs[msgs.length - 1]
              const assistantMsg = {
                role: 'assistant',
                content: data.answer,
                sources: data.sources || [],
                simulations: data.simulations || null,
              }
              // token events already added an assistant message → update it
              // no token events → last is still user message → append assistant message
              if (last.role === 'assistant') {
                return [...msgs.slice(0, -1), { ...last, ...assistantMsg }]
              }
              return [...msgs, assistantMsg]
            })
            setLoadingChatId(null)
            setStreamingChatId(null)
            setChats(prev => prev.map(c =>
              c.id === chatId && c.title === 'New Chat'
                ? { ...c, title: text.slice(0, 40) }
                : c
            ))
            fetchSuggestions(data.answer)
          }
        }
      }
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, the AI service is unavailable. Please make sure it is running on port 8000.',
        sources: [],
      }])
    } finally {
      setLoadingChatId(null)
      setStreamingChatId(null)
      setStatusMessage('')
    }
  }

  function handleSaveForChat({ age, riskLevel, horizon, interests, holdings, _holdingsText }) {
    const label = riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)
    setPortfolioContext({ age, riskLevel, horizon, interests, holdings })
    const interestText = interests?.length ? ` · ${interests.join(', ')}` : ''
    const holdingsText = _holdingsText ?? ''
    setMessages(prev => [...prev, {
      role: 'system',
      content: `Age: ${age} · Risk: ${label} · Horizon: ${horizon} yr${interestText}${holdingsText}`,
      sources: [],
    }])
    setMode('chat')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  return (
    <div className="chat-page">
      <ChatSidebar
        chats={chats}
        activeChatId={activeChatId}
        editingChatId={editingChatId}
        editingTitle={editingTitle}
        editInputRef={editInputRef}
        onBack={onBack}
        onNewChat={createNewChat}
        onSelectChat={selectChat}
        onDeleteChat={deleteChat}
        onStartEditTitle={startEditTitle}
        onCommitEditTitle={commitEditTitle}
        onEditKeyDown={handleEditKeyDown}
        onEditTitleChange={setEditingTitle}
      />

      <div className="chat-main">
        <div className="chat-header">
          <div className="chat-tabs">
            <button className={`tab ${mode === 'chat' ? 'tab-active' : ''}`} onClick={() => setMode('chat')}>Chat</button>
            <button className={`tab ${mode === 'portfolio' ? 'tab-active' : ''}`} onClick={() => setMode('portfolio')}>
              My Profile
              {!portfolioContext && <span className="tab-badge">Set up</span>}
            </button>
          </div>
          <div className="chat-status"><span className="status-dot" />AI ready</div>
        </div>

        {mode === 'chat' && (
          <>
            <div className="chat-messages">
              {messages.map((msg, i) => (
                msg.role === 'system'
                  ? <div key={i} className="system-notice">{msg.content}</div>
                  : (
                    <div key={i} className={`bubble-wrap ${msg.role}`}>
                      {msg.role === 'assistant' && <div className="avatar">◈</div>}
                      <div className="bubble-content">
                        <div className={`bubble ${msg.role}`} dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                        {msg.simulations?.length > 0 && (
                          <div className="simulation-group">
                            {msg.simulations.map((sim, i) => <SimulationCard key={i} simulation={sim} />)}
                          </div>
                        )}
                        {msg.sources?.length > 0 && <SourcesPanel sources={msg.sources} />}
                      </div>
                    </div>
                  )
              ))}
              {loadingChatId === activeChatId && (
                <div className="bubble-wrap assistant">
                  <div className="avatar">◈</div>
                  <div className="bubble assistant typing-status">
                    <span /><span /><span />
                    {statusMessage && <span className="status-label">{statusMessage}</span>}
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            <SuggestionBar
              suggestions={suggestions}
              isEmptyState={messages.length === 1 && messages[0].role === 'assistant'}
              visible={!loadingChatId && !streamingChatId}
              onSelect={(text) => handleSend(text)}
            />
            <div className="chat-input-bar">
              <textarea
                className="chat-input"
                placeholder="Ask about ETFs, risk, rebalancing..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
              />
              <button className="chat-send" onClick={() => handleSend()} disabled={!input.trim() || !!loadingChatId || !!streamingChatId}>
                Send →
              </button>
            </div>
          </>
        )}

        {mode === 'portfolio' && <PortfolioForm onSaveForChat={handleSaveForChat} onClear={() => setPortfolioContext(null)} savedProfile={portfolioContext} />}
      </div>
    </div>
  )
}
