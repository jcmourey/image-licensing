import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react(), // Default React plugin configuration
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
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.log('Proxy error:', err);
          });

          proxy.on('proxyReq', (_, req) => {
            console.log(`📤 REQUEST: ${req.method} ${req.url}`);

            if (req.method === 'PUT' || req.method === 'POST' || req.method === 'PATCH') {
              let body = '';
              req.on('data', chunk => (body += chunk));
              req.on('end', () => {
                try {
                  console.log('📤 REQUEST BODY:', JSON.stringify(JSON.parse(body), null, 2));
                } catch {
                  console.log('📤 REQUEST BODY:', body || '[unavailable]');
                }
              });
            }
          });

          proxy.on('proxyRes', (proxyRes, req) => {
            console.log(`📥 RESPONSE: ${req.method} ${req.url} - Status: ${proxyRes.statusCode}`);

            // let body = '';
            // proxyRes.on('data', chunk => (body += chunk));
            // proxyRes.on('end', () => {
            //   try {
            //     console.log('📥 RESPONSE BODY:', body ? JSON.stringify(JSON.parse(body), null, 2) : '[empty]');
            //   } catch {
            //     console.log('📥 RESPONSE BODY:', body || '[unavailable]');
            //   }
            // });
          });
        }
      }
    },
    allowedHosts: ['macstudiojeancharles.local', 'localhost', 'ds1821.local'],
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