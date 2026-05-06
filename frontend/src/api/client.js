import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000',
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response, // если всё хорошо — просто возвращаем ответ
  (error) => {
    if (error.response?.status === 401) {
      // Токен просрочен или невалиден — чистим localStorage
      localStorage.removeItem('token')
      // Перенаправляем на логин
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default client
