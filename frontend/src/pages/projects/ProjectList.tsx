import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

interface Project {
  id: string
  name: string
  description: string
  status: string
  created_at: string
}

function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Fetch projects from API
    setLoading(false)
  }, [])

  if (loading) {
    return <div className="p-4">Loading projects...</div>
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Projects</h1>
        <Link
          to="/projects/new"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Create Project
        </Link>
      </div>

      {projects.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No projects found</p>
          <Link
            to="/projects/new"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Create Your First Project
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {projects.map((project) => (
            <div key={project.id} className="border rounded-lg p-4 hover:shadow-md">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">
                    <Link to={`/projects/${project.id}`} className="hover:text-blue-500">
                      {project.name}
                    </Link>
                  </h3>
                  <p className="text-gray-600 mt-1">{project.description}</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Created: {new Date(project.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  project.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {project.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ProjectList
