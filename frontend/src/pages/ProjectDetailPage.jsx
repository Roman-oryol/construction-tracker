import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getMaterials, createMaterial, deleteMaterial } from '../api/materials'

function StockBadge({ status }) {
  const styles = {
    ok: 'bg-green-100 text-green-700',
    low: 'bg-yellow-100 text-yellow-700',
    critical: 'bg-red-100 text-red-700',
  }
  const labels = {
    ok: 'В норме',
    low: 'Мало',
    critical: 'Критично',
  }

  return (
    <span className={`text-xs font-medium px-2 py-1 rounded-full ${styles[status]}`}>
      {labels[status]}
    </span>
  )
}

export default function ProjectDetailPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  const [materials, setMaterials] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [showForm, setShowForm] = useState(false)
  const [newName, setNewName] = useState('')
  const [newUnit, setNewUnit] = useState('')
  const [newThreshold, setNewThreshold] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [creating, setCreating] = useState(false)

  const projectIdNum = Number(projectId)

  useEffect(() => {
    fetchMaterials()
  }, [projectId])

  const fetchMaterials = async () => {
    try {
      setLoading(true)
      const response = await getMaterials(projectIdNum)
      setMaterials(response.data)
    } catch (err) {
      setError('Не удалось загрузить материалы')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    setCreating(true)
    try {
      const response = await createMaterial({
        name: newName,
        unit: newUnit,
        low_stock_threshold: parseFloat(newThreshold) || 0,
        description: newDescription || null,
        project_id: projectIdNum,
      })
      setMaterials((prev) => [...prev, response.data])
      setNewName('')
      setNewUnit('')
      setNewThreshold('')
      setNewDescription('')
      setShowForm(false)
    } catch (err) {
      setError('Не удалось создать материал')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Удалить материал? Все завозы и списания также будут удалены.')) return
    try {
      await deleteMaterial(id)
      setMaterials((prev) => prev.filter((m) => m.id !== id))
    } catch (err) {
      setError('Не удалось удалить материал')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">Загрузка...</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Материалы</h2>
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Отмена' : '+ Новый материал'}
        </button>
      </div>

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="bg-white rounded-xl shadow-sm p-6 mb-6 flex flex-col gap-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Название</label>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              required
              placeholder="Цемент М400"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Единица измерения
            </label>
            <input
              type="text"
              value={newUnit}
              onChange={(e) => setNewUnit(e.target.value)}
              required
              placeholder="мешок, м³, тонна..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Порог низкого остатка
            </label>
            <input
              type="number"
              value={newThreshold}
              onChange={(e) => setNewThreshold(e.target.value)}
              min="0"
              step="0.001"
              placeholder="0"
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

      {materials.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <p className="text-gray-400 text-lg">Материалов пока нет</p>
          <p className="text-gray-400 text-sm mt-1">Нажмите «+ Новый материал» чтобы начать</p>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {materials.map((material) => (
            <div
              key={material.id}
              className="bg-white rounded-xl shadow-sm p-6 flex justify-between items-center"
            >
              <div
                onClick={() => navigate(`/projects/${projectId}/materials/${material.id}`)}
                className="cursor-pointer flex-1"
              >
                <div className="flex items-center gap-3">
                  <h3 className="text-lg font-semibold text-gray-800 hover:text-blue-600 transition-colors">
                    {material.name}
                  </h3>
                  <StockBadge status={material.stock_status} />
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Остаток:{' '}
                  <span className="font-medium text-gray-700">
                    {material.current_stock} {material.unit}
                  </span>
                  {material.low_stock_threshold > 0 && (
                    <span className="ml-2 text-gray-400">
                      (порог: {material.low_stock_threshold} {material.unit})
                    </span>
                  )}
                </p>
                {material.description && (
                  <p className="text-sm text-gray-400 mt-1 italic">{material.description}</p>
                )}
              </div>

              <button
                onClick={() => handleDelete(material.id)}
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
