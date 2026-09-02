import { Routes, Route } from 'react-router-dom'
import Navbar from '../components/common/Navbar'
import { ProtectedRoute } from './ProtectedRoute'
import Home from '../pages/Home'
import Courses from '../pages/Courses'
import CourseDetail from '../pages/CourseDetail'
import Products from '../pages/Products'
import ProductDetail from '../pages/ProductDetail'
import Login from '../pages/Login'
import Register from '../pages/Register'
import Dashboard from '../pages/student/Dashboard'
import MyCourses from '../pages/student/MyCourses'
import MyPurchases from '../pages/student/MyPurchases'
import PaymentSuccess from '../pages/PaymentSuccess'
import PaymentFailure from '../pages/PaymentFailure'
import AdminDashboard from '../pages/admin/Dashboard'
import ManageCourses from '../pages/admin/ManageCourses'
import CreateCourse from '../pages/admin/CreateCourse'
import EditCourse from '../pages/admin/EditCourse'
import ManageProducts from '../pages/admin/ManageProducts'
import CreateProduct from '../pages/admin/CreateProduct'
import EditProduct from '../pages/admin/EditProduct'

function AppRoutes() {
  return (
    <>
      <Navbar />
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/courses" element={<Courses />} />
        <Route path="/courses/:slug" element={<CourseDetail />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:slug" element={<ProductDetail />} />

        {/* Protected student routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/my-courses" element={<MyCourses />} />
          <Route path="/my-purchases" element={<MyPurchases />} />
          <Route path="/payment/success" element={<PaymentSuccess />} />
          <Route path="/payment/failure" element={<PaymentFailure />} />
        </Route>

        {/* Protected admin routes */}
        <Route element={<ProtectedRoute requireAdmin />}>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/courses" element={<ManageCourses />} />
          <Route path="/admin/courses/create" element={<CreateCourse />} />
          <Route path="/admin/courses/:id/edit" element={<EditCourse />} />
          <Route path="/admin/products" element={<ManageProducts />} />
          <Route path="/admin/products/create" element={<CreateProduct />} />
          <Route path="/admin/products/:id/edit" element={<EditProduct />} />
        </Route>
      </Routes>
    </>
  )
}

export default AppRoutes
