import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// The FastAPI backend runs on port 8000 (`uvicorn main:app --reload --port 8000` in backend/).
// Set BACKEND_URL to point the dev proxy somewhere else.
export default defineConfig(({ mode }) => {
  const backend = loadEnv(mode, '.', '').BACKEND_URL || 'http://127.0.0.1:8000'
  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': backend,
        '/media': backend,
      },
    },
  }
})
