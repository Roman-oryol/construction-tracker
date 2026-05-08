import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProjectsProvider } from './context/ProjectsContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'

import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProjectsPage from './pages/ProjectsPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import MaterialDetailPage from './pages/MaterialDetailPage'

function ProtectedLayout({ children }) {
  return (
    <ProtectedRoute>
      <ProjectsProvider>
        <Layout>{children}</Layout>
      </ProjectsProvider>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

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
