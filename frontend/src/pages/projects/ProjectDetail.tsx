import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

interface Project {
  id: string
  name: string
  description: string
  status: string
  created_at: string
}

function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Fetch project from API
    setLoading(false)
  }, [id])

  if (loading) {
    return <div className="p-4">Loading project...</div>
  }

  if (!project) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-2xl font-bold mb-4">Project Not Found</h1>
        <Link to="/projects" className="text-blue-500 hover:underline">
          Back to Projects
        </Link>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex items-center mb-6">
        <Link to="/projects" className="text-blue-500 hover:underline mr-4">
          ← Back to Projects
        </Link>
        <h1 className="text-2xl font-bold">{project.name}</h1>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-2">Description</h3>
            <p className="text-gray-600">{project.description}</p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">Status</h3>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              project.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            }`}>
              {project.status}
            </span>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">Created</h3>
            <p className="text-gray-600">{new Date(project.created_at).toLocaleString()}</p>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Project Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link to={`/agents?project=${id}`} className="bg-blue-50 hover:bg-blue-100 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-800">Agents</h3>
            <p className="text-blue-600 text-sm">Manage AI agents</p>
          </Link>
          <Link to={`/chat?project=${id}`} className="bg-green-50 hover:bg-green-100 p-4 rounded-lg">
            <h3 className="font-semibold text-green-800">Chat</h3>
            <p className="text-green-600 text-sm">Communicate with agents</p>
          </Link>
          <Link to={`/artifacts?project=${id}`} className="bg-purple-50 hover:bg-purple-100 p-4 rounded-lg">
            <h3 className="font-semibold text-purple-800">Artifacts</h3>
            <p className="text-purple-600 text-sm">View generated artifacts</p>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default ProjectDetail
