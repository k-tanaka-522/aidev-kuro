import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from '../App'
import { useAuthStore } from '../stores/authStore'

// Mock the auth store
jest.mock('../stores/authStore')
const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>

// Mock the pages to avoid complex rendering
jest.mock('../pages/auth/LoginPage', () => {
  return function MockLoginPage() {
    return <div data-testid="login-page">Login Page</div>
  }
})

jest.mock('../pages/Dashboard', () => {
  return function MockDashboard() {
    return <div data-testid="dashboard">Dashboard</div>
  }
})

jest.mock('../components/Layout', () => {
  return function MockLayout({ children }: { children: React.ReactNode }) {
    return <div data-testid="layout">{children}</div>
  }
})

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

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders login page when user is not authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      user: null,
      token: null,
      login: jest.fn(),
      logout: jest.fn(),
    })

    renderWithProviders(<App />)

    expect(screen.getByTestId('login-page')).toBeInTheDocument()
    expect(screen.queryByTestId('layout')).not.toBeInTheDocument()
  })

  it('renders dashboard when user is authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      user: {
        user_id: 'test-user',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user'
      },
      token: 'test-token',
      login: jest.fn(),
      logout: jest.fn(),
    })

    renderWithProviders(<App />)

    expect(screen.getByTestId('layout')).toBeInTheDocument()
    expect(screen.getByTestId('dashboard')).toBeInTheDocument()
    expect(screen.queryByTestId('login-page')).not.toBeInTheDocument()
  })

  it('redirects to dashboard from root when authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      user: {
        user_id: 'test-user',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user'
      },
      token: 'test-token',
      login: jest.fn(),
      logout: jest.fn(),
    })

    renderWithProviders(<App />)

    // Should render dashboard since / redirects to /dashboard
    expect(screen.getByTestId('dashboard')).toBeInTheDocument()
  })
})