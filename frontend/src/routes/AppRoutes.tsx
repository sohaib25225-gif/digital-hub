import { Routes, Route } from 'react-router-dom'
import Home from '../pages/Home'
import Courses from '../pages/Courses'
import Products from '../pages/Products'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/courses" element={<Courses />} />
      <Route path="/products" element={<Products />} />
      {/* Additional routes will be added in Phase 1B */}
    </Routes>
  )
}

export default AppRoutes
