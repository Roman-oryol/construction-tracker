import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useProjects } from '../context/ProjectsContext'

export default function Layout({ children }) {
  const { projects } = useProjects()
  const { logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const match = location.pathname.match(/^\/projects\/(\d+)/)
  const activeProjectId = match ? parseInt(match[1]) : null
  const isOnProjects = location.pathname === '/projects'

  const displayName = localStorage.getItem('userDisplayName') ?? 'Пользователь'

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* ── Боковая панель ── */}
      <aside className="w-56 min-h-screen bg-white shadow-sm flex flex-col shrink-0">
        {/* Логотип */}
        <div className="px-4 py-5 border-b border-gray-200">
          <h1 className="text-lg font-bold text-gray-800">Прораб</h1>
          <p className="text-xs text-gray-400 mt-0.5">Учёт материалов</p>
        </div>

        {/* Навигация */}
        <nav className="flex-1 py-3 overflow-y-auto">
          <button
            onClick={() => navigate('/projects')}
            className={`w-full text-left px-4 py-2 text-sm transition-colors ${
              isOnProjects
                ? 'bg-blue-50 text-blue-600 font-medium'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
            }`}
          >
            Все объекты
          </button>

          {projects.length > 0 && (
            <div className="mt-3">
              <p className="px-4 mb-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
                Объекты
              </p>
              {projects.map((project) => (
                <button
                  key={project.id}
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className={`w-full text-left px-4 py-2 text-sm transition-colors truncate ${
                    project.id === activeProjectId
                      ? 'bg-blue-50 text-blue-600 font-medium'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
                  }`}
                >
                  {project.name}
                </button>
              ))}
            </div>
          )}
        </nav>

        {/* Пользователь + выход */}
        <div className="px-4 py-3 border-t border-gray-200">
          <p className="text-sm text-gray-700 font-medium mb-1 truncate" title={displayName}>
            {displayName}
          </p>
          <button
            onClick={logout}
            className="text-sm text-gray-400 hover:text-red-500 transition-colors"
          >
            Выйти
          </button>
        </div>
      </aside>

      {/* ── Основной контент ── */}
      <div className="flex-1 min-w-0">{children}</div>
    </div>
  )
}
