import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'

import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProjectsPage from './pages/ProjectsPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import MaterialDetailPage from './pages/MaterialDetailPage'

// Все защищённые страницы получают Layout с сайдбаром
function ProtectedLayout({ children }) {
  return (
    <ProtectedRoute>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Публичные маршруты — без Layout */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Защищённые маршруты — с Layout */}
          <Route
            path="/projects"
            element={
              <ProtectedLayout>
                <ProjectsPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/projects/:projectId"
            element={
              <ProtectedLayout>
                <ProjectDetailPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/projects/:projectId/materials/:materialId"
            element={
              <ProtectedLayout>
                <MaterialDetailPage />
              </ProtectedLayout>
            }
          />

          <Route path="/" element={<Navigate to="/projects" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
