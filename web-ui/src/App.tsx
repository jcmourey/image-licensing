// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)
//
//   return (
//     <>
//       <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.tsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }

import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import ImageRows from "./pages/ImageRows.tsx"
import TailWindTest from "./components/TailwindTest.tsx"
import MatchRows from "./components/MatchRows.tsx";

export default function App() {
    return (
        <Router>
            {/* Remove any default styles that might conflict with Tailwind */}
            <div className="min-h-screen bg-white">
                <Routes>
                    <Route path="/" element={<ImageRows/>}/>
                    <Route path="/test" element={<TailWindTest/>}/>
                    <Route path="/image/:imageId/:selectedMatchId/matches" element={<MatchRows />}/>
                </Routes>
            </div>
        </Router>
    )
}
