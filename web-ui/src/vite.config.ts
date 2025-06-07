    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
        // Don't rewrite the path to keep the /api prefix
        // rewrite: (path) => path.replace(/^\/api/, '/api'),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.error('PROXY ERROR:', err);
          });
          proxy.on('proxyReq', (_proxyReq, req, _res) => {
            console.log('Sending Request:', req.method, req.url);
            if (req.method === 'PUT' || req.method === 'POST') {
              console.warn('Request Body:', req.body);
            }
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from:', req.url, 'Status:', proxyRes.statusCode);
            if (proxyRes.statusCode >= 400) {
              console.error('ERROR RESPONSE:', proxyRes.statusCode, proxyRes.statusMessage);
            }
          });
        },
        debug: true,
      }
    },
