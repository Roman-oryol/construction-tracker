import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProjects, createProject, deleteProject } from '../api/projects'
import { useAuth } from '../context/AuthContext'

export default function ProjectsPage() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Состояние для формы создания проекта
  const [showForm, setShowForm] = useState(false)
  const [newName, setNewName] = useState('')
  const [newAddress, setNewAddress] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [creating, setCreating] = useState(false)

  const { logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const response = await getProjects()
      setProjects(response.data)
    } catch (err) {
      setError('Не удалось загрузить проекты')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    setCreating(true)
    try {
      const response = await createProject({
        name: newName,
        address: newAddress,
        description: newDescription,
      })
      // Добавляем новый проект в конец списка без перезапроса всех проектов
      setProjects((prev) => [...prev, response.data])
      setNewName('')
      setNewAddress('')
      setShowForm(false)
    } catch (err) {
      setError('Не удалось создать проект')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Удалить проект?')) return
    try {
      await deleteProject(id)
      // Фильтруем удалённый проект из локального стейта
      setProjects((prev) => prev.filter((p) => p.id !== id))
    } catch (err) {
      setError('Не удалось удалить проект')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-500">Загрузка...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Навбар */}
      <nav className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">БудТрекер</h1>
        <button
          onClick={logout}
          className="text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          Выйти
        </button>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Мои проекты</h2>
          <button
            onClick={() => setShowForm((prev) => !prev)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {showForm ? 'Отмена' : '+ Новый проект'}
          </button>
        </div>

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        {/* Форма создания проекта — показываем только если showForm = true */}
        {showForm && (
          <form
            onSubmit={handleCreate}
            className="bg-white rounded-xl shadow-sm p-6 mb-6 flex flex-col gap-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Название проекта
              </label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Адрес (необязательно)
              </label>
              <input
                type="text"
                value={newAddress}
                onChange={(e) => setNewAddress(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Описание (необязательно)
              </label>
              <textarea
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                rows={2}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              type="submit"
              disabled={creating}
              className="bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {creating ? 'Создание...' : 'Создать'}
            </button>
          </form>
        )}

        {/* Список проектов */}
        {projects.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <p className="text-gray-400 text-lg">Проектов пока нет</p>
            <p className="text-gray-400 text-sm mt-1">Нажмите «+ Новый проект» чтобы начать</p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {projects.map((project) => (
              <div
                key={project.id}
                className="bg-white rounded-xl shadow-sm p-6 flex justify-between items-center"
              >
                <div
                  // Клик по названию — переход на страницу проекта
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className="cursor-pointer"
                >
                  <h3 className="text-lg font-semibold text-gray-800 hover:text-blue-600 transition-colors">
                    {project.name}
                  </h3>
                  {project.address && (
                    <p className="text-sm text-gray-500 mt-1">{project.address}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(project.id)}
                  className="text-sm text-red-400 hover:text-red-600 transition-colors ml-4"
                >
                  Удалить
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
