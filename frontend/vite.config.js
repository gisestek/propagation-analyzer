import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// If backend runs at :8000, we proxy /api requests there
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
