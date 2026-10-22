import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { AgentProvider } from './context/AgentContext'
import { CartProvider } from './context/CartContext'
import App from './App'
import './index.css'

// Blindaje BFCache: al restaurar la página desde el Back-Forward Cache de Chrome,
// los WebSockets (Vite HMR), speechSynthesis/SpeechRecognition y las instancias del
// VoiceTurnManager quedan rotos o desincronizados, dejando la UI "zombi" donde los
// clicks no hacen nada. La recarga completa garantiza estado limpio y ses vivo.
window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    console.warn('[APP-LIFECYCLE] Página restaurada desde Back-Forward Cache: recargando para estado limpio...')
    window.location.reload()
  }
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <AgentProvider>
          <CartProvider>
            <App />
          </CartProvider>
        </AgentProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
)
