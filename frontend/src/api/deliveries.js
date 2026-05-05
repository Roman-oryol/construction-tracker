import client from './client'

export const getDeliveries = (materialId) =>
  client.get('/deliveries/', { params: { material_id: materialId } })

export const createDelivery = (data) => client.post('/deliveries/', data)

export const deleteDelivery = (id) => client.delete(`/deliveries/${id}`)
