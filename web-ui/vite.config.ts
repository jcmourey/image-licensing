import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(), // Default React plugin configuration
    tailwindcss(), // Add Tailwind CSS v4 plugin
  ],
  define: {
    // Define environment variables with default values
    'import.meta.env.VITE_SHOW_TAILWIND_TEST': JSON.stringify(process.env.VITE_SHOW_TAILWIND_TEST || 'false'),
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
        // Don't rewrite the path to keep the /api prefix
        // rewrite: (path) => path.replace(/^\/api/, '/api'),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (_proxyReq, req, _res) => {
            console.log('Sending Request:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from:', req.url, proxyRes.statusCode);
          });
        },
      }
    },
    allowedHosts: ['macstudiojeancharles.local', 'localhost'],
    // Add HMR settings
    hmr: {
      overlay: true,
    },
    // More aggressive file watching
    watch: {
      usePolling: true,
      interval: 100,
    }
  },
  // Add extra optimization settings
  optimizeDeps: {
    force: true,
  }
})