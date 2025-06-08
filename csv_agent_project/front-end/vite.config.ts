import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
    },
    headers: {
      'Content-Security-Policy': "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: mercadopago.com.br *.mercadopago.com.br mercadopago.com *.mercadopago.com mercadopago.com.co *.mercadopago.com.co js-agent.newrelic.com *.js-agent.newrelic.com siteintercept.qualtrics.com *.siteintercept.qualtrics.com http2.mlstatic.com *.http2.mlstatic.com googletagmanager.com *.googletagmanager.com google.com *.google.com mercadopago.cl *.mercadopago.cl mercadopago.com.mx *.mercadopago.com.mx hotjar.com *.hotjar.com mercadopago.com.pe *.mercadopago.com.pe mercadopago.com.uy *.mercadopago.com.uy mercadopago.com.ar *.mercadopago.com.ar static.hotjar.com *.static.hotjar.com mercadopago.com.ve *.mercadopago.com.ve newrelic.com *.newrelic.com gstatic.com *.gstatic.com;"
    }
  },
  build: {
    target: 'esnext',
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom']
  }
});