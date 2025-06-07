import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Mount the React app with proper HMR support
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

// Explicitly handle HMR
if (import.meta.hot) {
  import.meta.hot.accept();
}
