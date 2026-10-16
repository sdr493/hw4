import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './auth'
import { CatalogProvider } from './catalog'
import { ChatResultsProvider } from './chatResults'
import { PromoProvider } from './promoContext'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <PromoProvider>
          <CatalogProvider>
            <ChatResultsProvider>
              <App />
            </ChatResultsProvider>
          </CatalogProvider>
        </PromoProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
