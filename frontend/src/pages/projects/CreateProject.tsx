import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

function CreateProject() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      // TODO: Submit to API
      console.log('Creating project:', formData)
      navigate('/projects')
    } catch (error) {
      console.error('Error creating project:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="p-6">
      <div className="flex items-center mb-6">
        <Link to="/projects" className="text-blue-500 hover:underline mr-4">
          ← Back to Projects
        </Link>
        <h1 className="text-2xl font-bold">Create New Project</h1>
      </div>

      <div className="max-w-lg">
        <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-6">
          <div className="mb-4">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Project Name
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project name"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project description"
            />
          </div>

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading || !formData.name.trim()}
              className="bg-blue-500 hover:bg-blue-700 disabled:bg-gray-300 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              {loading ? 'Creating...' : 'Create Project'}
            </button>
            <Link
              to="/projects"
              className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateProject
