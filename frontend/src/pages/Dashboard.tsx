import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  PlusIcon, 
  FolderIcon, 
  CpuChipIcon, 
  DocumentTextIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

import { projectsApi } from '@/services/api'

export default function Dashboard() {
  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list({ page: 1, page_size: 5 }),
  })

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['project-stats'],
    queryFn: () => projectsApi.getStats(),
  })

  const projectsList = projects?.data?.projects || []
  const projectStats = stats?.data || {}

  const statCards = [
    {
      name: 'Total Projects',
      value: projectStats.total_projects || 0,
      icon: FolderIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Active Projects', 
      value: projectStats.active_projects || 0,
      icon: ChartBarIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Completed Tasks',
      value: projectStats.completed_tasks || 0,
      icon: DocumentTextIcon,
      color: 'bg-purple-500',
    },
    {
      name: 'Active Agents',
      value: 3, // Mock data
      icon: CpuChipIcon,
      color: 'bg-orange-500',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome to your AgentDev Platform</p>
        </div>
        <Link
          to="/projects/new"
          className="btn-primary"
        >
          <PlusIcon className="mr-2 h-4 w-4" />
          New Project
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.name} className="card p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    {stat.name}
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {statsLoading ? '...' : stat.value}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Projects */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Recent Projects</h3>
            <Link
              to="/projects"
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              View all
            </Link>
          </div>
        </div>
        <div className="p-6">
          {projectsLoading ? (
            <div className="text-center py-4">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
            </div>
          ) : projectsList.length === 0 ? (
            <div className="text-center py-8">
              <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No projects</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating a new project.
              </p>
              <div className="mt-6">
                <Link to="/projects/new" className="btn-primary">
                  <PlusIcon className="mr-2 h-4 w-4" />
                  New Project
                </Link>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {projectsList.map((project: any) => (
                <Link
                  key={project.project_id}
                  to={`/projects/${project.project_id}`}
                  className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-900">
                        {project.name}
                      </h4>
                      <p className="text-sm text-gray-500 mt-1">
                        {project.description || 'No description'}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        project.status === 'active' 
                          ? 'bg-green-100 text-green-800'
                          : project.status === 'completed'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {project.status}
                      </span>
                      <div className="text-xs text-gray-500">
                        {Math.round(project.progress_percentage || 0)}%
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <Link
          to="/projects/new"
          className="card p-6 hover:bg-gray-50 transition-colors cursor-pointer"
        >
          <div className="flex items-center">
            <FolderIcon className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Start New Project</h3>
              <p className="text-sm text-gray-500">Create a new development project</p>
            </div>
          </div>
        </Link>

        <Link
          to="/agents"
          className="card p-6 hover:bg-gray-50 transition-colors cursor-pointer"
        >
          <div className="flex items-center">
            <CpuChipIcon className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Manage Agents</h3>
              <p className="text-sm text-gray-500">Configure AI agents</p>
            </div>
          </div>
        </Link>

        <Link
          to="/chat"
          className="card p-6 hover:bg-gray-50 transition-colors cursor-pointer"
        >
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Team Chat</h3>
              <p className="text-sm text-gray-500">Collaborate with agents</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}