import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import Layout from '@/components/Layout'
import LoginPage from '@/pages/auth/LoginPage'
import Dashboard from '@/pages/Dashboard'
import ProjectList from '@/pages/projects/ProjectList'
import ProjectDetail from '@/pages/projects/ProjectDetail'
import CreateProject from '@/pages/projects/CreateProject'
import AgentManagement from '@/pages/agents/AgentManagement'
import ChatView from '@/pages/chat/ChatView'
import ArtifactList from '@/pages/artifacts/ArtifactList'

function App() {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/projects" element={<ProjectList />} />
        <Route path="/projects/new" element={<CreateProject />} />
        <Route path="/projects/:id" element={<ProjectDetail />} />
        <Route path="/agents" element={<AgentManagement />} />
        <Route path="/chat" element={<ChatView />} />
        <Route path="/artifacts" element={<ArtifactList />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  )
}

export default App