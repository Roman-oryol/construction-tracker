import { createContext, useContext, useEffect, useState } from 'react'
import { getProjects } from '../api/projects'

const ProjectsContext = createContext(null)

export function ProjectsProvider({ children }) {
  const [projects, setProjects] = useState([])

  const refreshProjects = async () => {
    try {
      const response = await getProjects()
      setProjects(response.data)
    } catch {
      // Если пользователь не залогинен,
      // этот запрос не выполнится (401 → редирект в client.js)
    }
  }

  // Загружаем проекты один раз при монтировании провайдера
  useEffect(() => {
    refreshProjects()
  }, [])

  return (
    <ProjectsContext.Provider value={{ projects, refreshProjects }}>
      {children}
    </ProjectsContext.Provider>
  )
}

export function useProjects() {
  return useContext(ProjectsContext)
}
