import { useState, useEffect } from 'react'

interface Artifact {
  id: string
  name: string
  type: 'code' | 'document' | 'diagram' | 'other'
  content: string
  created_at: string
  agent_name: string
}

function ArtifactList() {
  const [artifacts, setArtifacts] = useState<Artifact[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null)

  useEffect(() => {
    // TODO: Fetch artifacts from API
    setLoading(false)
  }, [])

  if (loading) {
    return <div className="p-4">Loading artifacts...</div>
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Artifacts</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-lg font-semibold mb-4">Artifact List</h2>
          {artifacts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No artifacts found
            </div>
          ) : (
            <div className="space-y-3">
              {artifacts.map((artifact) => (
                <div 
                  key={artifact.id} 
                  className={`border rounded-lg p-4 cursor-pointer hover:shadow-md ${
                    selectedArtifact?.id === artifact.id ? 'border-blue-500 bg-blue-50' : ''
                  }`}
                  onClick={() => setSelectedArtifact(artifact)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold">{artifact.name}</h3>
                      <p className="text-sm text-gray-600">Created by: {artifact.agent_name}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(artifact.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      artifact.type === 'code' ? 'bg-green-100 text-green-800' :
                      artifact.type === 'document' ? 'bg-blue-100 text-blue-800' :
                      artifact.type === 'diagram' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {artifact.type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <h2 className="text-lg font-semibold mb-4">Artifact Content</h2>
          {selectedArtifact ? (
            <div className="bg-white border rounded-lg p-4">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-semibold text-lg">{selectedArtifact.name}</h3>
                  <p className="text-sm text-gray-600">Type: {selectedArtifact.type}</p>
                </div>
                <button className="text-blue-500 hover:text-blue-700 text-sm">
                  Download
                </button>
              </div>
              <div className="bg-gray-50 rounded p-3 max-h-96 overflow-y-auto">
                <pre className="text-sm whitespace-pre-wrap">{selectedArtifact.content}</pre>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 border rounded-lg p-8 text-center text-gray-500">
              Select an artifact to view its content
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ArtifactList
