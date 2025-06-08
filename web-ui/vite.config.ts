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
        // Don't rewrite the path to keep the /api prefix
        // rewrite: (path) => path.replace(/^\/api/, '/api'),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('Proxy error:', err);
          });
          
          proxy.on('proxyReq', (_proxyReq, req, _res) => {
            console.log(`📤 REQUEST: ${req.method} ${req.url}`);
            
            // Log request body for PUT/POST requests that might contain used_in data
            if ((req.method === 'PUT' || req.method === 'POST') && req.url && req.url.includes('used_in')) {
              let body = '';
              req.on('data', (chunk) => {
                body += chunk;
              });
              
              req.on('end', () => {
                try {
                  const jsonBody = JSON.parse(body);
                  console.log(`📤 REQUEST BODY: ${JSON.stringify(jsonBody, null, 2)}`);
                  console.log(`📤 used_in value: "${jsonBody.used_in}" (${typeof jsonBody.used_in})`);
                } catch (e) {
                  console.log(`📤 REQUEST BODY: Unable to parse JSON - ${body}`);
                }
              });
            }
          });
          
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log(`📥 RESPONSE: ${req.method} ${req.url} - Status: ${proxyRes.statusCode}`);
            
            // Log response body for requests related to used_in
            if (req.url &&req.url.includes('used_in')) {
              let body = '';
              proxyRes.on('data', (chunk) => {
                body += chunk;
              });
              
              proxyRes.on('end', () => {
                try {
                  if (body) {
                    const jsonBody = JSON.parse(body);
                    console.log(`📥 RESPONSE BODY: ${JSON.stringify(jsonBody, null, 2)}`);
                  } else {
                    console.log(`📥 RESPONSE BODY: Empty response`);
                  }
                } catch (e) {
                  console.log(`📥 RESPONSE BODY: ${body}`);
                }
              });
            }
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