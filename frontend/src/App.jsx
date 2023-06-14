import { Routes, Route, BrowserRouter } from "react-router-dom"
import LoginPage from './login.jsx'
import Content from './content.jsx'


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/content" element={<Content />} />
      </Routes>
    </BrowserRouter>
  )
};

export default App