import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  FileText, 
  Upload, 
  History, 
  Menu, 
  X,
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  FolderOpen,
  Loader2,
  AlertCircle,
  RefreshCw,
  FolderPlus
} from 'lucide-react';
import { useProjects } from '../hooks/useProjects';
import { ProjectCreationModal } from './ProjectCreationModal';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarMinimized, setSidebarMinimized] = useState(false);
  const [projectDropdownOpen, setProjectDropdownOpen] = useState(false);
  const [createProjectModalOpen, setCreateProjectModalOpen] = useState(false);
  const [createProjectLoading, setCreateProjectLoading] = useState(false);
  const location = useLocation();

  // Use real backend data for projects
  const { 
    data: projects, 
    loading: projectsLoading, 
    error: projectsError,
    selectedProject,
    setSelectedProject,
    refetch: refetchProjects,
    createProject
  } = useProjects();

  // Store previous project ID to detect changes and force page refresh
  const [prevProjectId, setPrevProjectId] = React.useState<string | undefined>(selectedProject?.id);

  // Force page refresh when project changes
  React.useEffect(() => {
    if (selectedProject?.id && prevProjectId && selectedProject.id !== prevProjectId) {
      console.log('Layout: Project changed from', prevProjectId, 'to', selectedProject.id, '- refreshing page');
      window.location.reload();
    }
    setPrevProjectId(selectedProject?.id);
  }, [selectedProject?.id, prevProjectId]);

  // Handle project creation
  const handleCreateProject = async (projectData: { name: string; default_start_url: string }) => {
    try {
      setCreateProjectLoading(true);
      await createProject(projectData);
      setCreateProjectModalOpen(false);
    } catch (error) {
      console.error('Failed to create project:', error);
      // Error handling is done in the modal component
      throw error;
    } finally {
      setCreateProjectLoading(false);
    }
  };

  const navigation = [
    { name: 'Test cases', href: '/', icon: FileText },
    { name: 'Create test', href: '/create', icon: Upload },
    { name: 'Test runs', href: '/runs', icon: History },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    
    // Handle test case detail pages - show Test cases as active
    if (path === '/' && location.pathname.startsWith('/test-details/')) return true;
    
    // Handle test run detail pages - show Test runs as active  
    if (path === '/runs' && location.pathname.startsWith('/runs/')) return true;
    
    return location.pathname === path;
  };

  const sidebarWidth = sidebarMinimized ? 'w-20' : 'w-72';
  const contentMargin = sidebarMinimized ? 'lg:ml-20' : 'lg:ml-72';

  const currentProject = selectedProject;

  const ProjectDropdown = () => {
    return (
      <div className="relative">
        <button
          type="button"
          onClick={() => setProjectDropdownOpen(!projectDropdownOpen)}
          disabled={projectsLoading}
          className="w-full bg-white border border-dashed border-gray-300 rounded-lg px-4 py-3 text-left flex items-center justify-between hover:border-gray-400 transition-colors focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span className="font-medium text-gray-600 truncate flex items-center">
            {projectsLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Loading projects...
              </>
            ) : currentProject?.name || 'Select Project'}
          </span>
          <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform flex-shrink-0 ${projectDropdownOpen ? 'rotate-180' : ''}`} />
        </button>
        
        {projectDropdownOpen && (
          <>
            {/* Backdrop to close dropdown when clicking outside */}
            <div 
              className="fixed inset-0 z-[9998]" 
              onClick={() => setProjectDropdownOpen(false)}
            />
            {/* Dropdown menu positioned absolutely within the sidebar */}
            <div 
              className="absolute top-full left-0 right-0 mt-1 bg-white border border-dashed border-gray-300 rounded-lg overflow-hidden shadow-xl z-[9999] max-h-60 overflow-y-auto"
            >
              {projectsLoading ? (
                <div className="px-4 py-3 flex items-center justify-center text-gray-500">
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Loading projects...
                </div>
              ) : projectsError ? (
                <div className="px-4 py-3">
                  <div className="flex items-center text-red-600 mb-2">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    Failed to load projects
                  </div>
                  <button
                    onClick={() => {
                      refetchProjects();
                    }}
                    className="flex items-center text-sm text-indigo-600 hover:text-indigo-700"
                  >
                    <RefreshCw className="w-3 h-3 mr-1" />
                    Retry
                  </button>
                </div>
              ) : projects && projects.length > 0 ? (
                <>
                  {/* Existing Projects */}
                  {projects.map((project) => (
                    <button
                      key={project.id}
                      type="button"
                      onClick={() => {
                        console.log('Layout: Selecting project:', project.name, project.id);
                        setSelectedProject(project);
                        setProjectDropdownOpen(false);
                      }}
                      className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                        project.id === selectedProject?.id ? 'bg-indigo-50' : ''
                      }`}
                    >
                      <span className="font-medium text-gray-600 truncate">{project.name}</span>
                    </button>
                  ))}
                  
                  {/* Separator */}
                  <div className="px-4 py-3">
                    <div className="border-t border-gray-200"></div>
                  </div>
                  
                  {/* Create New Project Button - Primary style at bottom */}
                  <div className="px-4 pb-4">
                    <button
                      type="button"
                      onClick={() => {
                        setCreateProjectModalOpen(true);
                        setProjectDropdownOpen(false);
                      }}
                      className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
                    >
                      <FolderPlus className="w-4 h-4" />
                      <span>Create New Project</span>
                    </button>
                  </div>
                </>
              ) : (
                <>
                  {/* No projects message */}
                  <div className="px-4 py-3 text-gray-500 text-center text-sm">
                    No projects found
                  </div>
                  
                  {/* Create First Project Button - Primary style */}
                  <div className="px-4 pb-4">
                    <button
                      type="button"
                      onClick={() => {
                        setCreateProjectModalOpen(true);
                        setProjectDropdownOpen(false);
                      }}
                      className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
                    >
                      <FolderPlus className="w-4 h-4" />
                      <span>Create Your First Project</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          </>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 relative">
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setSidebarOpen(true)}
          className="bg-white/90 backdrop-blur-sm p-2 rounded-lg border border-gray-200"
        >
          <Menu className="w-6 h-6 text-gray-700" />
        </button>
      </div>

      {/* Sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`sidebar-container fixed left-0 top-0 h-full ${sidebarWidth} bg-white/80 backdrop-blur-xl border-r border-dashed border-gray-300 z-50 transform transition-all duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0`}>
        
        {/* Logo and controls */}
        {!sidebarMinimized && (
          <div className="flex items-center justify-between px-6 py-3">
            <div className="flex items-center">
              <img 
                src="/bugninja.svg" 
                alt="Bugninja" 
                className="transition-all duration-300 w-24 h-10" 
              />
            </div>
            <div className="flex items-center space-x-2">
              {/* Minimize button (desktop only) */}
              <button
                onClick={() => setSidebarMinimized(!sidebarMinimized)}
                className="hidden lg:flex w-12 h-12 items-center justify-center rounded-lg hover:bg-gray-100 transition-colors"
                title="Minimize sidebar"
              >
                <ChevronLeft className="w-5 h-5 text-gray-500" />
              </button>
              {/* Close button (mobile only) */}
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden w-12 h-12 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
          </div>
        )}
        
        {/* Minimized expand button */}
        {sidebarMinimized && (
          <div className="px-2 py-1 pt-3">
            <button
              onClick={() => setSidebarMinimized(false)}
              className="w-12 h-12 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors mx-auto"
              title="Expand sidebar"
            >
              <ChevronRight className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        )}

        {/* Dashed separator */}
        <div className={`mb-4 ${sidebarMinimized ? 'mx-4' : 'mx-4'}`}>
          <div className="border-t border-dashed border-gray-300"></div>
        </div>

        {/* Project Selector */}
        {!sidebarMinimized && (
          <div className="px-4 mb-4">
            <ProjectDropdown />
          </div>
        )}
        
        {/* Project selector for minimized state */}
        {sidebarMinimized && (
          <div className="flex justify-center">
            <button
              onClick={() => setSidebarMinimized(false)}
              className="w-12 h-12 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors"
              title={currentProject?.name || 'Select Project'}
            >
              <FolderOpen className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        )}

        {/* Navigation */}
        <nav className="px-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center ${
                  sidebarMinimized 
                    ? 'justify-center w-12 h-12 mx-auto' 
                    : 'space-x-3 px-4 py-3'
                } rounded-lg transition-colors group ${
                  active 
                    ? 'bg-indigo-600 text-white' 
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
                title={sidebarMinimized ? item.name : undefined}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 ${active ? 'text-white' : 'text-gray-500 group-hover:text-gray-700'}`} />
                {!sidebarMinimized && (
                  <span className="font-medium whitespace-nowrap">{item.name}</span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Bottom section */}
        <div className="absolute bottom-0 left-0 right-0 p-3">
          <div className="border-t border-dashed border-gray-300 pt-3">
            <div className={`flex items-center ${
              sidebarMinimized 
                ? 'justify-center w-12 h-12 mx-auto' 
                : 'space-x-3 px-4 py-3'
            } rounded-lg hover:bg-gray-100 transition-all duration-300 cursor-pointer`}
            title={sidebarMinimized ? "Help & Support" : undefined}>
              <HelpCircle className="w-5 h-5 text-gray-500 flex-shrink-0" />
              {!sidebarMinimized && (
                <span className="font-medium text-gray-600 whitespace-nowrap opacity-100 transition-opacity duration-300">Help & Support</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className={`${contentMargin} min-h-screen transition-all duration-300`}>
        <main className="p-6 lg:p-8">
          {children}
        </main>
      </div>
      
      {/* Project Creation Modal */}
      <ProjectCreationModal
        isOpen={createProjectModalOpen}
        onClose={() => setCreateProjectModalOpen(false)}
        onCreateProject={handleCreateProject}
        loading={createProjectLoading}
      />
    </div>
  );
};

export default Layout; 