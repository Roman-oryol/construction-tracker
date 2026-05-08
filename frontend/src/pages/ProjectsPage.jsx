import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createProject, deleteProject } from '../api/projects'
import { useProjects } from '../context/ProjectsContext'

export default function ProjectsPage() {
  // Берём проекты и функцию обновления из контекста.
  // Теперь после создания/удаления проекта достаточно вызвать
  // refreshProjects() — и сайдбар обновится автоматически.
  const { projects, refreshProjects } = useProjects()

  const [showForm, setShowForm] = useState(false)
  const [newName, setNewName] = useState('')
  const [newAddress, setNewAddress] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState(null)

  const navigate = useNavigate()

  const handleCreate = async (e) => {
    e.preventDefault()
    setCreating(true)
    try {
      await createProject({
        name: newName,
        address: newAddress,
        description: newDescription,
      })
      // Вместо ручного обновления локального стейта — просто
      // перезапрашиваем список. Обновятся и сайдбар, и эта страница.
      await refreshProjects()
      setNewName('')
      setNewAddress('')
      setNewDescription('')
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
      await refreshProjects()
    } catch (err) {
      setError('Не удалось удалить проект')
    }
  }

  return (
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

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="bg-white rounded-xl shadow-sm p-6 mb-6 flex flex-col gap-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Название проекта</label>
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
              <div onClick={() => navigate(`/projects/${project.id}`)} className="cursor-pointer">
                <h3 className="text-lg font-semibold text-gray-800 hover:text-blue-600 transition-colors">
                  {project.name}
                </h3>
                {project.address && <p className="text-sm text-gray-500 mt-1">{project.address}</p>}
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
  )
}
