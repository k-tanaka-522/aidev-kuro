import { useState, useEffect } from 'react'

interface Message {
  id: string
  content: string
  sender: 'user' | 'agent'
  timestamp: string
  agent_name?: string
}

function ChatView() {
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // TODO: Fetch chat history from API
  }, [])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessage.trim()) return

    setLoading(true)
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: newMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, userMessage])
    setNewMessage('')

    try {
      // TODO: Send message to API and get agent response
      setTimeout(() => {
        const agentResponse: Message = {
          id: (Date.now() + 1).toString(),
          content: 'This is a mock response from the agent.',
          sender: 'agent',
          timestamp: new Date().toISOString(),
          agent_name: 'PM Agent'
        }
        setMessages(prev => [...prev, agentResponse])
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error sending message:', error)
      setLoading(false)
    }
  }

  return (
    <div className="p-6 h-full flex flex-col">
      <h1 className="text-2xl font-bold mb-6">Chat with Agents</h1>
      
      <div className="flex-1 bg-white rounded-lg shadow p-4 mb-4 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No messages yet. Start a conversation!
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user' 
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}>
                  {message.sender === 'agent' && message.agent_name && (
                    <div className="text-xs font-semibold mb-1">{message.agent_name}</div>
                  )}
                  <div>{message.content}</div>
                  <div className={`text-xs mt-1 ${
                    message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <form onSubmit={handleSendMessage} className="flex gap-2">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !newMessage.trim()}
          className="bg-blue-500 hover:bg-blue-700 disabled:bg-gray-300 text-white font-bold py-2 px-4 rounded"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  )
}

export default ChatView
