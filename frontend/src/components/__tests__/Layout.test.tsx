import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Layout from '../Layout'
import { useAuthStore } from '../../stores/authStore'

// Mock the auth store
jest.mock('../../stores/authStore')
const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>

// Mock useLocation
const mockLocation = {
  pathname: '/dashboard',
  search: '',
  hash: '',
  state: null,
  key: 'default'
}

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useLocation: () => mockLocation,
  Link: ({ children, to, className }: any) => (
    <a href={to} className={className} data-testid={`link-${to}`}>
      {children}
    </a>
  ),
}))

const renderWithRouter = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {ui}
    </BrowserRouter>
  )
}

describe('Layout', () => {
  const mockLogout = jest.fn()
  
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseAuthStore.mockReturnValue({
      user: {
        user_id: 'test-user',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user'
      },
      token: 'test-token',
      isAuthenticated: true,
      login: jest.fn(),
      logout: mockLogout,
    })
  })

  it('renders layout with navigation and user info', () => {
    renderWithRouter(
      <Layout>
        <div data-testid="child-content">Test Content</div>
      </Layout>
    )

    // Check if main elements are rendered
    expect(screen.getByText('AgentDev Platform')).toBeInTheDocument()
    expect(screen.getByText('Test User')).toBeInTheDocument()
    expect(screen.getByText('test@example.com')).toBeInTheDocument()
    expect(screen.getByTestId('child-content')).toBeInTheDocument()
  })

  it('renders all navigation links', () => {
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )

    // Check navigation links
    expect(screen.getByTestId('link-/dashboard')).toBeInTheDocument()
    expect(screen.getByTestId('link-/projects')).toBeInTheDocument()
    expect(screen.getByTestId('link-/agents')).toBeInTheDocument()
    expect(screen.getByTestId('link-/chat')).toBeInTheDocument()
    expect(screen.getByTestId('link-/artifacts')).toBeInTheDocument()
  })

  it('highlights active navigation item', () => {
    // Set location to projects page
    mockLocation.pathname = '/projects'
    
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )

    const projectsLink = screen.getByTestId('link-/projects')
    expect(projectsLink).toHaveClass('sidebar-link-active')
  })

  it('shows inactive state for non-active navigation items', () => {
    // Dashboard is active
    mockLocation.pathname = '/dashboard'
    
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )

    const projectsLink = screen.getByTestId('link-/projects')
    expect(projectsLink).toHaveClass('sidebar-link-inactive')
  })

  it('handles logout when logout button is clicked', () => {
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )

    const logoutButton = screen.getByTitle('Logout')
    fireEvent.click(logoutButton)

    expect(mockLogout).toHaveBeenCalledTimes(1)
  })

  it('renders user information correctly', () => {
    const customUser = {
      user_id: 'custom-user',
      email: 'custom@example.com',
      name: 'Custom User',
      role: 'admin'
    }

    mockUseAuthStore.mockReturnValue({
      user: customUser,
      token: 'test-token',
      isAuthenticated: true,
      login: jest.fn(),
      logout: mockLogout,
    })

    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )

    expect(screen.getByText('Custom User')).toBeInTheDocument()
    expect(screen.getByText('custom@example.com')).toBeInTheDocument()
  })

  it('handles missing user gracefully', () => {
    mockUseAuthStore.mockReturnValue({
      user: null,
      token: null,
      isAuthenticated: false,
      login: jest.fn(),
      logout: mockLogout,
    })

    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )

    // Should not crash and still render the layout structure
    expect(screen.getByText('AgentDev Platform')).toBeInTheDocument()
  })

  it('renders children content correctly', () => {
    const testContent = (
      <div>
        <h1>Test Page</h1>
        <p>This is test content</p>
      </div>
    )

    renderWithRouter(<Layout>{testContent}</Layout>)

    expect(screen.getByText('Test Page')).toBeInTheDocument()
    expect(screen.getByText('This is test content')).toBeInTheDocument()
  })

  it('applies correct CSS classes for layout structure', () => {
    const { container } = renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )

    // Check for key CSS classes that define the layout
    const sidebar = container.querySelector('.fixed.inset-y-0.left-0')
    const mainContent = container.querySelector('.pl-64')
    
    expect(sidebar).toBeInTheDocument()
    expect(mainContent).toBeInTheDocument()
  })
})