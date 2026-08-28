import React from 'react'
import ReactDOM from 'react-dom/client'
import ChatApp from './ChatApp.jsx'


// Busca el div donde se montará la app en base.html
const rootElement = document.getElementById('react-chat-root')

if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <ChatApp />
    </React.StrictMode>,
  )
}
