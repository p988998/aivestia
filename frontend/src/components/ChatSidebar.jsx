export default function ChatSidebar({
  chats,
  activeChatId,
  editingChatId,
  editingTitle,
  editInputRef,
  onBack,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onStartEditTitle,
  onCommitEditTitle,
  onEditKeyDown,
  onEditTitleChange,
}) {
  return (
    <div className="chat-sidebar">
      <div className="sidebar-top">
        <button className="btn-back-sidebar" onClick={onBack}>← Back</button>
        <button className="btn-new-chat" onClick={onNewChat}>+ New Chat</button>
      </div>
      <div className="sidebar-chat-list">
        {chats.map(chat => (
          <div
            key={chat.id}
            className={`sidebar-chat-item ${chat.id === activeChatId ? 'sidebar-chat-active' : ''}`}
            onClick={() => editingChatId !== chat.id && onSelectChat(chat.id)}
          >
            {editingChatId === chat.id ? (
              <input
                ref={editInputRef}
                className="sidebar-chat-edit-input"
                value={editingTitle}
                onChange={e => onEditTitleChange(e.target.value)}
                onBlur={() => onCommitEditTitle(chat.id)}
                onKeyDown={e => onEditKeyDown(e, chat.id)}
                onClick={e => e.stopPropagation()}
                maxLength={60}
              />
            ) : (
              <span
                className="sidebar-chat-title"
                onDoubleClick={e => onStartEditTitle(chat, e)}
                title="Double-click to rename"
              >{chat.title || 'New Chat'}</span>
            )}
            <button
              className="sidebar-chat-delete"
              onClick={e => onDeleteChat(chat.id, e)}
              title="Delete chat"
            >×</button>
          </div>
        ))}
      </div>
    </div>
  )
}
