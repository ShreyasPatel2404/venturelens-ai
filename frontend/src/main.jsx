// // CURRENT (causes double mount in dev):
// import { StrictMode } from 'react'
// import { createRoot } from 'react-dom/client'
// import App from './App.jsx'

// createRoot(document.getElementById('root')).render(
//   <StrictMode>
//     <App />
//   </StrictMode>,
// )

// CHANGE TO:
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import './index.css'  // ← must be here

createRoot(document.getElementById('root')).render(
  <App />
)