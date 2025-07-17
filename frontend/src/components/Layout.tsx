import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  HomeIcon, 
  FolderIcon, 
  ChatBubbleLeftEllipsisIcon,
  CpuChipIcon,
  DocumentTextIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline'
import { useAuthStore } from '@/stores/authStore'
import clsx from 'clsx'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Projects', href: '/projects', icon: FolderIcon },
  { name: 'Agents', href: '/agents', icon: CpuChipIcon },
  { name: 'Chat', href: '/chat', icon: ChatBubbleLeftEllipsisIcon },
  { name: 'Artifacts', href: '/artifacts', icon: DocumentTextIcon },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-16 items-center justify-center border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">AgentDev Platform</h1>
        </div>
        
        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href || 
                (item.href !== '/dashboard' && location.pathname.startsWith(item.href))
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    isActive ? 'sidebar-link-active' : 'sidebar-link-inactive'
                  )}
                >
                  <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </nav>
        
        {/* User menu */}
        <div className="absolute bottom-0 w-full border-t border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">{user?.name}</p>
              <p className="text-xs text-gray-500">{user?.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="ml-3 inline-flex items-center p-2 text-gray-400 hover:text-gray-600"
              title="Logout"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}