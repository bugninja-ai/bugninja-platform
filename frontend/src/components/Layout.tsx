import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { createPortal } from 'react-dom';
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
  FolderOpen
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarMinimized, setSidebarMinimized] = useState(false);
  const [projectDropdownOpen, setProjectDropdownOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState('bugninja-banking');
  const location = useLocation();

  // Mock project data - will be replaced with backend data later
  const projects = [
    { id: 'bugninja-banking', name: 'Bugninja Banking' },
    { id: 'ecommerce-platform', name: 'E-commerce Platform' },
    { id: 'healthcare-app', name: 'Healthcare App' },
    { id: 'fintech-wallet', name: 'Fintech Wallet' },
  ];

  const navigation = [
    { name: 'Test cases', href: '/', icon: FileText },
    { name: 'Create test', href: '/create', icon: Upload },
    { name: 'Test runs', href: '/history', icon: History },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    
    // Handle test case detail pages - show Test cases as active
    if (path === '/' && location.pathname.startsWith('/test-details/')) return true;
    
    // Handle test run detail pages - show Test runs as active  
    if (path === '/history' && location.pathname.startsWith('/history/')) return true;
    
    return location.pathname === path;
  };

  const sidebarWidth = sidebarMinimized ? 'w-20' : 'w-72';
  const contentMargin = sidebarMinimized ? 'lg:ml-20' : 'lg:ml-72';

  const currentProject = projects.find(p => p.id === selectedProject);

  const ProjectDropdown = () => {
    const [buttonRef, setButtonRef] = useState<HTMLButtonElement | null>(null);
    
    const getDropdownPosition = () => {
      if (!buttonRef) return { top: 0, left: 0 };
      
      const rect = buttonRef.getBoundingClientRect();
      return {
        top: rect.bottom + window.scrollY + 4,
        left: rect.left + window.scrollX
      };
    };

    return (
      <div className="relative">
        <button
          ref={setButtonRef}
          type="button"
          onClick={() => setProjectDropdownOpen(!projectDropdownOpen)}
          className="w-full bg-white border border-dashed border-gray-300 rounded-lg px-4 py-3 text-left flex items-center justify-between hover:border-gray-400 transition-colors focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <span className="font-medium text-gray-600 truncate">{currentProject?.name || 'Select Project'}</span>
          <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform flex-shrink-0 ${projectDropdownOpen ? 'rotate-180' : ''}`} />
        </button>
        
        {projectDropdownOpen && createPortal(
          <>
            <div 
              className="fixed inset-0 z-[9998]" 
              onClick={() => setProjectDropdownOpen(false)}
            />
            <div 
              className="fixed bg-white border border-dashed border-gray-300 rounded-lg overflow-hidden shadow-xl z-[9999]"
              style={{
                top: `${getDropdownPosition().top}px`,
                left: `${getDropdownPosition().left}px`,
                width: `${buttonRef?.offsetWidth || 200}px`,
                maxHeight: '240px',
                overflowY: 'auto'
              }}
            >
              {projects.map((project) => (
                <button
                  key={project.id}
                  type="button"
                  onClick={() => {
                    setSelectedProject(project.id);
                    setProjectDropdownOpen(false);
                  }}
                  className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                    project.id === selectedProject ? 'bg-indigo-50' : ''
                  }`}
                >
                  <span className="font-medium text-gray-600 truncate">{project.name}</span>
                </button>
              ))}
            </div>
          </>,
          document.body
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
    </div>
  );
};

export default Layout; 