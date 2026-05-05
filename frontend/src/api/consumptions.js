import client from './client'

export const getConsumptions = (materialId) =>
  client.get('/consumptions/', { params: { material_id: materialId } })

export const createConsumption = (data) => client.post('/consumptions/', data)

export const deleteConsumption = (id) => client.delete(`/consumptions/${id}`)
