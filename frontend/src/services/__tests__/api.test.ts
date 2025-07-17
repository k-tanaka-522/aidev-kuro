import axios from 'axios'
import { authApi, projectsApi, agentsApi, messagesApi, artifactsApi } from '../api'
import { useAuthStore } from '../../stores/authStore'

// Mock axios
jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

// Mock the auth store
jest.mock('../../stores/authStore')
const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>

// Mock axios.create
const mockAxiosInstance = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  interceptors: {
    request: {
      use: jest.fn(),
    },
    response: {
      use: jest.fn(),
    },
  },
}

mockedAxios.create.mockReturnValue(mockAxiosInstance as any)

describe('API Services', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    
    // Mock auth store state
    mockUseAuthStore.mockReturnValue({
      token: 'test-token',
      user: {
        user_id: 'test-user',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user'
      },
      isAuthenticated: true,
      login: jest.fn(),
      logout: jest.fn(),
    })
  })

  describe('authApi', () => {
    it('login makes correct API call', async () => {
      const mockResponse = {
        data: {
          access_token: 'new-token',
          user_info: {
            user_id: 'user-123',
            email: 'test@example.com',
            name: 'Test User'
          }
        }
      }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await authApi.login('test@example.com', 'password')

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/v1/auth/login', {
        email: 'test@example.com',
        password: 'password'
      })
      expect(result).toEqual(mockResponse)
    })

    it('logout makes correct API call', async () => {
      const mockResponse = { data: { message: 'Logged out' } }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await authApi.logout()

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/v1/auth/logout')
      expect(result).toEqual(mockResponse)
    })

    it('refreshToken makes correct API call', async () => {
      const mockResponse = {
        data: {
          access_token: 'refreshed-token',
          user_info: { user_id: 'user-123' }
        }
      }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await authApi.refreshToken('refresh-token')

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/v1/auth/refresh', {
        refresh_token: 'refresh-token'
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('projectsApi', () => {
    it('list makes correct API call with params', async () => {
      const mockResponse = {
        data: {
          projects: [{ project_id: 'proj-1', name: 'Test Project' }],
          total: 1
        }
      }
      mockAxiosInstance.get.mockResolvedValue(mockResponse)

      const params = { status: 'active', page: 1, page_size: 10 }
      const result = await projectsApi.list(params)

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/v1/projects/', {
        params
      })
      expect(result).toEqual(mockResponse)
    })

    it('get makes correct API call', async () => {
      const mockResponse = {
        data: { project_id: 'proj-1', name: 'Test Project' }
      }
      mockAxiosInstance.get.mockResolvedValue(mockResponse)

      const result = await projectsApi.get('proj-1')

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/v1/projects/proj-1')
      expect(result).toEqual(mockResponse)
    })

    it('create makes correct API call', async () => {
      const projectData = {
        name: 'New Project',
        description: 'Test description'
      }
      const mockResponse = {
        data: { project_id: 'proj-new', ...projectData }
      }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await projectsApi.create(projectData)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/v1/projects/', projectData)
      expect(result).toEqual(mockResponse)
    })

    it('update makes correct API call', async () => {
      const updateData = { name: 'Updated Project' }
      const mockResponse = {
        data: { project_id: 'proj-1', ...updateData }
      }
      mockAxiosInstance.put.mockResolvedValue(mockResponse)

      const result = await projectsApi.update('proj-1', updateData)

      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/api/v1/projects/proj-1', updateData)
      expect(result).toEqual(mockResponse)
    })

    it('delete makes correct API call', async () => {
      mockAxiosInstance.delete.mockResolvedValue({ data: {} })

      const result = await projectsApi.delete('proj-1')

      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/api/v1/projects/proj-1')
      expect(result.data).toEqual({})
    })

    it('start makes correct API call', async () => {
      const mockResponse = {
        data: { project_id: 'proj-1', status: 'active' }
      }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await projectsApi.start('proj-1')

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/v1/projects/proj-1/start')
      expect(result).toEqual(mockResponse)
    })

    it('getStats makes correct API call', async () => {
      const mockResponse = {
        data: {
          total_projects: 5,
          active_projects: 2,
          completed_projects: 3
        }
      }
      mockAxiosInstance.get.mockResolvedValue(mockResponse)

      const result = await projectsApi.getStats()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/v1/projects/stats/summary')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('agentsApi', () => {
    it('list makes correct API call with project filter', async () => {
      const mockResponse = {
        data: [{ agent_id: 'agent-1', name: 'PM Agent' }]
      }
      mockAxiosInstance.get.mockResolvedValue(mockResponse)

      const result = await agentsApi.list('proj-1')

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/v1/agents/', {
        params: { project_id: 'proj-1' }
      })
      expect(result).toEqual(mockResponse)
    })

    it('create makes correct API call', async () => {
      const agentData = {
        name: 'New Agent',
        agent_type: 'pm',
        project_id: 'proj-1'
      }
      const mockResponse = {
        data: { agent_id: 'agent-new', ...agentData }
      }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await agentsApi.create(agentData)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/v1/agents/', agentData)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('messagesApi', () => {
    it('getChannels makes correct API call', async () => {
      const mockResponse = {
        data: [{ channel_id: 'channel-1', name: 'General' }]
      }
      mockAxiosInstance.get.mockResolvedValue(mockResponse)

      const result = await messagesApi.getChannels('proj-1')

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/v1/messages/channels', {
        params: { project_id: 'proj-1' }
      })
      expect(result).toEqual(mockResponse)
    })

    it('getMessages makes correct API call with params', async () => {
      const mockResponse = {
        data: [{ message_id: 'msg-1', content: 'Hello' }]
      }
      mockAxiosInstance.get.mockResolvedValue(mockResponse)

      const params = { limit: 50, before: 'msg-0' }
      const result = await messagesApi.getMessages('channel-1', params)

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/v1/messages/channel-1', {
        params
      })
      expect(result).toEqual(mockResponse)
    })

    it('sendMessage makes correct API call', async () => {
      const messageData = {
        channel_id: 'channel-1',
        content: 'Hello world',
        message_type: 'text'
      }
      const mockResponse = {
        data: { message_id: 'msg-new', ...messageData }
      }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await messagesApi.sendMessage(messageData)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/v1/messages/', messageData)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('artifactsApi', () => {
    it('list makes correct API call with filters', async () => {
      const mockResponse = {
        data: [{ artifact_id: 'art-1', name: 'Document' }]
      }
      mockAxiosInstance.get.mockResolvedValue(mockResponse)

      const params = { project_id: 'proj-1', artifact_type: 'document' }
      const result = await artifactsApi.list(params)

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/v1/artifacts/', {
        params
      })
      expect(result).toEqual(mockResponse)
    })

    it('create makes correct API call', async () => {
      const artifactData = {
        name: 'New Artifact',
        artifact_type: 'document',
        project_id: 'proj-1'
      }
      const mockResponse = {
        data: { artifact_id: 'art-new', ...artifactData }
      }
      mockAxiosInstance.post.mockResolvedValue(mockResponse)

      const result = await artifactsApi.create(artifactData)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/v1/artifacts/', artifactData)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('API interceptors', () => {
    it('sets up request interceptor for authentication', () => {
      // Verify that interceptors were set up
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled()
    })

    it('sets up response interceptor for error handling', () => {
      // Verify that interceptors were set up
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled()
    })
  })
})