import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getMaterial } from '../api/materials'
import { getDeliveries, createDelivery, deleteDelivery } from '../api/deliveries'
import { getConsumptions, createConsumption, deleteConsumption } from '../api/consumptions'

function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

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

export default function MaterialDetailPage() {
  const { projectId, materialId } = useParams()
  const navigate = useNavigate()

  const [material, setMaterial] = useState(null)
  const [deliveries, setDeliveries] = useState([])
  const [consumptions, setConsumptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [activeTab, setActiveTab] = useState('deliveries')

  // Состояние формы — одна форма для обоих типов операций,
  // тип определяется активной вкладкой
  const [showForm, setShowForm] = useState(false)
  const [quantity, setQuantity] = useState('')
  const [date, setDate] = useState('')
  const [comment, setComment] = useState('')
  // supplier для завозов, brigade для списаний
  const [supplierOrBrigade, setSupplierOrBrigade] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const materialIdNum = Number(materialId)

  useEffect(() => {
    fetchAll()
  }, [materialId])

  const fetchAll = async () => {
    try {
      setLoading(true)
      const [materialRes, deliveriesRes, consumptionsRes] = await Promise.all([
        getMaterial(materialIdNum),
        getDeliveries(materialIdNum),
        getConsumptions(materialIdNum),
      ])
      setMaterial(materialRes.data)
      setDeliveries(deliveriesRes.data)
      setConsumptions(consumptionsRes.data)
    } catch (err) {
      setError('Не удалось загрузить данные')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      if (activeTab === 'deliveries') {
        const response = await createDelivery({
          material_id: materialIdNum,
          quantity: parseFloat(quantity),
          delivered_at: date || null,
          supplier: supplierOrBrigade || null,
          comment: comment || null,
        })
        setDeliveries((prev) => [...prev, response.data])
      } else {
        const response = await createConsumption({
          material_id: materialIdNum,
          quantity: parseFloat(quantity),
          consumed_at: date || null,
          brigade: supplierOrBrigade || null,
          comment: comment || null,
        })
        setConsumptions((prev) => [...prev, response.data])
      }

      // Перезагружаем материал, чтобы получить актуальный current_stock и stock_status
      const materialRes = await getMaterial(materialIdNum)
      setMaterial(materialRes.data)

      // Сбрасываем форму
      setQuantity('')
      setDate('')
      setComment('')
      setSupplierOrBrigade('')
      setShowForm(false)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Не удалось сохранить')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteDelivery = async (id) => {
    if (!confirm('Удалить запись о завозе?')) return
    try {
      await deleteDelivery(id)
      setDeliveries((prev) => prev.filter((d) => d.id !== id))
      // Перезагружаем материал чтобы обновить остаток
      const materialRes = await getMaterial(materialIdNum)
      setMaterial(materialRes.data)
    } catch (err) {
      setError('Не удалось удалить запись')
    }
  }

  const handleDeleteConsumption = async (id) => {
    if (!confirm('Удалить запись о списании?')) return
    try {
      await deleteConsumption(id)
      setConsumptions((prev) => prev.filter((c) => c.id !== id))
      const materialRes = await getMaterial(materialIdNum)
      setMaterial(materialRes.data)
    } catch (err) {
      setError('Не удалось удалить запись')
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
        <h1
          onClick={() => navigate('/projects')}
          className="text-xl font-bold text-gray-800 cursor-pointer hover:text-blue-600 transition-colors"
        >
          БудТрекер
        </h1>
        <button
          onClick={() => navigate(`/projects/${projectId}`)}
          className="text-sm text-gray-500 hover:text-blue-600 transition-colors"
        >
          ← К материалам
        </button>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Карточка материала с текущим остатком */}
        {material && (
          <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold text-gray-800">{material.name}</h2>
              <StockBadge status={material.stock_status} />
            </div>
            <p className="text-gray-500">
              Текущий остаток:{' '}
              <span className="font-semibold text-gray-800">
                {material.current_stock} {material.unit}
              </span>
              {material.low_stock_threshold > 0 && (
                <span className="ml-2 text-gray-400 text-sm">
                  (порог: {material.low_stock_threshold} {material.unit})
                </span>
              )}
            </p>
            {material.description && (
              <p className="text-sm text-gray-400 mt-2 italic">{material.description}</p>
            )}
          </div>
        )}

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        {/* Вкладки + кнопка добавления */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex gap-2">
            <button
              onClick={() => {
                setActiveTab('deliveries')
                setShowForm(false)
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'deliveries'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              Завозы ({deliveries.length})
            </button>
            <button
              onClick={() => {
                setActiveTab('consumptions')
                setShowForm(false)
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'consumptions'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              Списания ({consumptions.length})
            </button>
          </div>

          <button
            onClick={() => setShowForm((prev) => !prev)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            {showForm ? 'Отмена' : activeTab === 'deliveries' ? '+ Завоз' : '+ Списание'}
          </button>
        </div>

        {/* Форма добавления */}
        {showForm && (
          <form
            onSubmit={handleSubmit}
            className="bg-white rounded-xl shadow-sm p-6 mb-6 flex flex-col gap-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Количество ({material?.unit})
              </label>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                required
                min="0.001"
                step="0.001"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {activeTab === 'deliveries' ? 'Поставщик' : 'Бригада'} (необязательно)
              </label>
              <input
                type="text"
                value={supplierOrBrigade}
                onChange={(e) => setSupplierOrBrigade(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Дата (необязательно, по умолчанию — сейчас)
              </label>
              <input
                type="datetime-local"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Комментарий (необязательно)
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={2}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {submitting ? 'Сохранение...' : 'Сохранить'}
            </button>
          </form>
        )}

        {/* Список записей активной вкладки */}
        {activeTab === 'deliveries' ? (
          deliveries.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <p className="text-gray-400">Завозов пока нет</p>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {deliveries.map((delivery) => (
                <div
                  key={delivery.id}
                  className="bg-white rounded-xl shadow-sm p-4 flex justify-between items-center"
                >
                  <div>
                    <p className="font-semibold text-gray-800">
                      +{delivery.quantity} {material?.unit}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      {formatDate(delivery.delivered_at)}
                      {delivery.supplier && ` · ${delivery.supplier}`}
                    </p>
                    {delivery.comment && (
                      <p className="text-sm text-gray-400 mt-1 italic">{delivery.comment}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDeleteDelivery(delivery.id)}
                    className="text-sm text-red-400 hover:text-red-600 transition-colors ml-4"
                  >
                    Удалить
                  </button>
                </div>
              ))}
            </div>
          )
        ) : consumptions.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <p className="text-gray-400">Списаний пока нет</p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {consumptions.map((consumption) => (
              <div
                key={consumption.id}
                className="bg-white rounded-xl shadow-sm p-4 flex justify-between items-center"
              >
                <div>
                  <p className="font-semibold text-gray-800">
                    -{consumption.quantity} {material?.unit}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    {formatDate(consumption.consumed_at)}
                    {consumption.brigade && ` · ${consumption.brigade}`}
                  </p>
                  {consumption.comment && (
                    <p className="text-sm text-gray-400 mt-1 italic">{consumption.comment}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteConsumption(consumption.id)}
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
