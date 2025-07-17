import { useAuthStore } from '../authStore'

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('AuthStore', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Reset store state
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false
    })
  })

  it('has correct initial state', () => {
    const state = useAuthStore.getState()
    
    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })

  it('logs in user correctly', () => {
    const mockUser = {
      user_id: 'test-user-123',
      email: 'test@example.com',
      name: 'Test User',
      role: 'user'
    }
    const mockToken = 'mock-jwt-token'

    const { login } = useAuthStore.getState()
    login(mockToken, mockUser)

    const state = useAuthStore.getState()
    expect(state.user).toEqual(mockUser)
    expect(state.token).toBe(mockToken)
    expect(state.isAuthenticated).toBe(true)
  })

  it('logs out user correctly', () => {
    // First login
    const mockUser = {
      user_id: 'test-user-123',
      email: 'test@example.com',
      name: 'Test User',
      role: 'user'
    }
    const mockToken = 'mock-jwt-token'

    const { login, logout } = useAuthStore.getState()
    login(mockToken, mockUser)

    // Verify logged in
    expect(useAuthStore.getState().isAuthenticated).toBe(true)

    // Then logout
    logout()

    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })

  it('persists state changes', () => {
    const mockUser = {
      user_id: 'test-user-123',
      email: 'test@example.com',
      name: 'Test User',
      role: 'user'
    }
    const mockToken = 'mock-jwt-token'

    const { login } = useAuthStore.getState()
    login(mockToken, mockUser)

    // Check if localStorage.setItem was called (persistence)
    // Note: The exact call depends on zustand's persist implementation
    expect(localStorageMock.setItem).toHaveBeenCalled()
  })

  it('handles user role correctly', () => {
    const adminUser = {
      user_id: 'admin-user-123',
      email: 'admin@example.com',
      name: 'Admin User',
      role: 'admin'
    }
    const mockToken = 'mock-jwt-token'

    const { login } = useAuthStore.getState()
    login(mockToken, adminUser)

    const state = useAuthStore.getState()
    expect(state.user?.role).toBe('admin')
  })

  it('maintains state consistency during multiple operations', () => {
    const user1 = {
      user_id: 'user-1',
      email: 'user1@example.com',
      name: 'User One',
      role: 'user'
    }
    const user2 = {
      user_id: 'user-2',
      email: 'user2@example.com',
      name: 'User Two',
      role: 'admin'
    }

    const { login, logout } = useAuthStore.getState()

    // Login user 1
    login('token1', user1)
    expect(useAuthStore.getState().user?.user_id).toBe('user-1')

    // Login user 2 (should replace user 1)
    login('token2', user2)
    expect(useAuthStore.getState().user?.user_id).toBe('user-2')
    expect(useAuthStore.getState().user?.role).toBe('admin')

    // Logout
    logout()
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
  })
})