import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '../Dashboard'
import { projectsApi } from '../../services/api'

// Mock the API
jest.mock('../../services/api')
const mockProjectsApi = projectsApi as jest.Mocked<typeof projectsApi>

// Mock react-router-dom Link
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Link: ({ children, to, className }: any) => (
    <a href={to} className={className} data-testid={`link-${to.replace('/', '')}`}>
      {children}
    </a>
  ),
}))

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {ui}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('Dashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders dashboard header and quick actions', () => {
    // Mock API responses
    mockProjectsApi.list.mockResolvedValue({
      data: { projects: [], total: 0, page: 1, page_size: 5, has_next: false }
    } as any)
    
    mockProjectsApi.getStats.mockResolvedValue({
      data: {
        total_projects: 0,
        active_projects: 0,
        completed_projects: 0,
        draft_projects: 0,
        total_tasks: 0,
        completed_tasks: 0,
        average_completion_rate: 0
      }
    } as any)

    renderWithProviders(<Dashboard />)

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Welcome to your AgentDev Platform')).toBeInTheDocument()
    expect(screen.getByTestId('link-projectsnew')).toBeInTheDocument()
  })

  it('displays stats cards with correct data', async () => {
    const mockStats = {
      total_projects: 5,
      active_projects: 3,
      completed_projects: 2,
      draft_projects: 0,
      total_tasks: 20,
      completed_tasks: 15,
      average_completion_rate: 75.0
    }

    mockProjectsApi.list.mockResolvedValue({
      data: { projects: [], total: 0, page: 1, page_size: 5, has_next: false }
    } as any)
    
    mockProjectsApi.getStats.mockResolvedValue({
      data: mockStats
    } as any)

    renderWithProviders(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument() // Total Projects
      expect(screen.getByText('3')).toBeInTheDocument() // Active Projects
      expect(screen.getByText('15')).toBeInTheDocument() // Completed Tasks
    })

    expect(screen.getByText('Total Projects')).toBeInTheDocument()
    expect(screen.getByText('Active Projects')).toBeInTheDocument()
    expect(screen.getByText('Completed Tasks')).toBeInTheDocument()
    expect(screen.getByText('Active Agents')).toBeInTheDocument()
  })

  it('displays recent projects when available', async () => {
    const mockProjects = [
      {
        project_id: 'proj-1',
        name: 'Test Project 1',
        description: 'First test project',
        status: 'active',
        progress_percentage: 50.0
      },
      {
        project_id: 'proj-2',
        name: 'Test Project 2',
        description: 'Second test project',
        status: 'completed',
        progress_percentage: 100.0
      }
    ]

    mockProjectsApi.list.mockResolvedValue({
      data: { 
        projects: mockProjects, 
        total: 2, 
        page: 1, 
        page_size: 5, 
        has_next: false 
      }
    } as any)
    
    mockProjectsApi.getStats.mockResolvedValue({
      data: {
        total_projects: 2,
        active_projects: 1,
        completed_projects: 1,
        draft_projects: 0,
        total_tasks: 10,
        completed_tasks: 8,
        average_completion_rate: 80.0
      }
    } as any)

    renderWithProviders(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('Test Project 1')).toBeInTheDocument()
      expect(screen.getByText('Test Project 2')).toBeInTheDocument()
      expect(screen.getByText('First test project')).toBeInTheDocument()
      expect(screen.getByText('Second test project')).toBeInTheDocument()
    })

    // Check status badges
    expect(screen.getByText('active')).toBeInTheDocument()
    expect(screen.getByText('completed')).toBeInTheDocument()

    // Check progress percentages
    expect(screen.getByText('50%')).toBeInTheDocument()
    expect(screen.getByText('100%')).toBeInTheDocument()
  })

  it('shows empty state when no projects exist', async () => {
    mockProjectsApi.list.mockResolvedValue({
      data: { projects: [], total: 0, page: 1, page_size: 5, has_next: false }
    } as any)
    
    mockProjectsApi.getStats.mockResolvedValue({
      data: {
        total_projects: 0,
        active_projects: 0,
        completed_projects: 0,
        draft_projects: 0,
        total_tasks: 0,
        completed_tasks: 0,
        average_completion_rate: 0
      }
    } as any)

    renderWithProviders(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('No projects')).toBeInTheDocument()
      expect(screen.getByText('Get started by creating a new project.')).toBeInTheDocument()
    })

    // Should show the create project button in empty state
    const createButtons = screen.getAllByText('New Project')
    expect(createButtons.length).toBeGreaterThan(0)
  })

  it('shows loading state initially', () => {
    // Make API calls hang
    mockProjectsApi.list.mockImplementation(() => new Promise(() => {}))
    mockProjectsApi.getStats.mockImplementation(() => new Promise(() => {}))

    renderWithProviders(<Dashboard />)

    // Should show loading indicators
    expect(screen.getByText('...')).toBeInTheDocument()
  })

  it('renders quick action cards', async () => {
    mockProjectsApi.list.mockResolvedValue({
      data: { projects: [], total: 0, page: 1, page_size: 5, has_next: false }
    } as any)
    
    mockProjectsApi.getStats.mockResolvedValue({
      data: {
        total_projects: 0,
        active_projects: 0,
        completed_projects: 0,
        draft_projects: 0,
        total_tasks: 0,
        completed_tasks: 0,
        average_completion_rate: 0
      }
    } as any)

    renderWithProviders(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('Start New Project')).toBeInTheDocument()
      expect(screen.getByText('Manage Agents')).toBeInTheDocument()
      expect(screen.getByText('Team Chat')).toBeInTheDocument()
    })

    expect(screen.getByText('Create a new development project')).toBeInTheDocument()
    expect(screen.getByText('Configure AI agents')).toBeInTheDocument()
    expect(screen.getByText('Collaborate with agents')).toBeInTheDocument()
  })

  it('handles API errors gracefully', async () => {
    // Mock API errors
    mockProjectsApi.list.mockRejectedValue(new Error('API Error'))
    mockProjectsApi.getStats.mockRejectedValue(new Error('Stats Error'))

    renderWithProviders(<Dashboard />)

    // Component should still render without crashing
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('displays correct project status colors', async () => {
    const mockProjects = [
      {
        project_id: 'proj-1',
        name: 'Active Project',
        status: 'active',
        progress_percentage: 50.0
      },
      {
        project_id: 'proj-2',
        name: 'Completed Project',
        status: 'completed',
        progress_percentage: 100.0
      },
      {
        project_id: 'proj-3',
        name: 'Draft Project',
        status: 'draft',
        progress_percentage: 0.0
      }
    ]

    mockProjectsApi.list.mockResolvedValue({
      data: { 
        projects: mockProjects, 
        total: 3, 
        page: 1, 
        page_size: 5, 
        has_next: false 
      }
    } as any)
    
    mockProjectsApi.getStats.mockResolvedValue({
      data: {
        total_projects: 3,
        active_projects: 1,
        completed_projects: 1,
        draft_projects: 1,
        total_tasks: 10,
        completed_tasks: 5,
        average_completion_rate: 50.0
      }
    } as any)

    renderWithProviders(<Dashboard />)

    await waitFor(() => {
      // Check for status badges with correct colors
      const activeStatus = screen.getByText('active')
      const completedStatus = screen.getByText('completed')
      const draftStatus = screen.getByText('draft')

      expect(activeStatus).toHaveClass('bg-green-100', 'text-green-800')
      expect(completedStatus).toHaveClass('bg-blue-100', 'text-blue-800')
      expect(draftStatus).toHaveClass('bg-gray-100', 'text-gray-800')
    })
  })
})