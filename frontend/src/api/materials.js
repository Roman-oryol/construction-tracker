import client from './client'

export const getMaterials = (projectId) =>
  client.get('/materials/', { params: { project_id: projectId } })

export const getMaterial = (id) => client.get(`/materials/${id}`)

export const createMaterial = (data) => client.post('/materials/', data)

export const updateMaterial = (id, data) => client.patch(`/materials/${id}`, data)

export const deleteMaterial = (id) => client.delete(`/materials/${id}`)
