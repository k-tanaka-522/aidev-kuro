import { useState, useEffect } from 'react'

interface Agent {
  id: string
  name: string
  type: 'PM' | 'Architect' | 'Security' | 'Custom'
  status: 'active' | 'inactive'
  created_at: string
}

function AgentManagement() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Fetch agents from API
    setLoading(false)
  }, [])

  if (loading) {
    return <div className="p-4">Loading agents...</div>
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Agent Management</h1>
        <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Create Agent
        </button>
      </div>

      {agents.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No agents found</p>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Create Your First Agent
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {agents.map((agent) => (
            <div key={agent.id} className="border rounded-lg p-4 hover:shadow-md">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{agent.name}</h3>
                  <p className="text-gray-600 mt-1">Type: {agent.type}</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Created: {new Date(agent.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {agent.status}
                  </span>
                  <button className="text-blue-500 hover:text-blue-700 text-sm">
                    Edit
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AgentManagement
