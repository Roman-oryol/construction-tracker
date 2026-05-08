import client from './client'

export const register = (email, password, name = null) =>
  client.post('/auth/register', { email, password })

export const login = async (email, password) => {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const response = await client.post('/auth/login', form)
  return response.data
}
