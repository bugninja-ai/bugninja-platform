import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Settings as SettingsIcon, 
  Monitor, 
  Key, 
  Trash2, 
  Loader2,
  Globe,
  Eye,
  EyeOff,
  Edit,
  Save,
  X as XIcon,
  AlertCircle
} from 'lucide-react';
import { useProjects } from '../hooks/useProjects';
import { DeleteConfirmationModal } from '../components/DeleteConfirmationModal';
import { settingsService, BrowserConfig, SecretValue, UpdateProjectData } from '../services/settingsService';
import { ProjectService } from '../services/projectService';

type SettingsSection = 'project' | 'browser-configs' | 'secret-values' | 'global' | 'integrations';

const Settings: React.FC = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState<SettingsSection>('project');
  const [browserConfigs, setBrowserConfigs] = useState<BrowserConfig[]>([]);
  const [secretValues, setSecretValues] = useState<SecretValue[]>([]);
  const [loading, setLoading] = useState(false);
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
  
  // Project editing state
  const [isEditingProject, setIsEditingProject] = useState(false);
  const [editingProject, setEditingProject] = useState<{
    name: string;
    default_start_url: string;
  }>({ name: '', default_start_url: '' });
  const [projectUpdateLoading, setProjectUpdateLoading] = useState(false);
  
  // Project deletion state
  const [showProjectDeleteModal, setShowProjectDeleteModal] = useState(false);
  const [projectDeleteLoading, setProjectDeleteLoading] = useState(false);
  const [projectDeleteError, setProjectDeleteError] = useState<string | null>(null);
  
  // Confirmation modal state
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    type: 'browser-config' | 'secret-value';
    item: BrowserConfig | SecretValue | null;
    loading: boolean;
    error: string | null;
  }>({
    isOpen: false,
    type: 'browser-config',
    item: null,
    loading: false,
    error: null,
  });

  const { selectedProject, refetch: refetchProjects } = useProjects();

  // Initialize editing project data when selectedProject changes
  useEffect(() => {
    if (selectedProject) {
      setEditingProject({
        name: selectedProject.name,
        default_start_url: selectedProject.default_start_url,
      });
    }
  }, [selectedProject]);

  // Fetch data when project changes or section changes
  useEffect(() => {
    if (selectedProject?.id) {
      if (activeSection === 'browser-configs') {
        fetchBrowserConfigs();
      } else if (activeSection === 'secret-values') {
        fetchSecretValues();
      }
    }
  }, [selectedProject?.id, activeSection]);

  const fetchBrowserConfigs = async () => {
    if (!selectedProject?.id) return;
    
    setLoading(true);
    try {
      const data = await settingsService.getBrowserConfigs(selectedProject.id);
      // Filter out any configs with null browser_config to prevent errors
      const validConfigs = data.filter(config => config.browser_config !== null);
      setBrowserConfigs(validConfigs);
    } catch (err) {
      console.error('Error fetching browser configs:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSecretValues = async () => {
    if (!selectedProject?.id) return;
    
    setLoading(true);
    try {
      const data = await settingsService.getSecretValues(selectedProject.id);
      setSecretValues(data);
    } catch (err) {
      console.error('Error fetching secret values:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBrowserConfig = async (config: BrowserConfig) => {
    setConfirmModal({
      isOpen: true,
      type: 'browser-config',
      item: config,
      loading: false,
      error: null,
    });
  };

  const handleDeleteSecretValue = async (secret: SecretValue) => {
    setConfirmModal({
      isOpen: true,
      type: 'secret-value',
      item: secret,
      loading: false,
      error: null,
    });
  };

  const confirmDelete = async () => {
    if (!confirmModal.item) return;

    setConfirmModal(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const result = confirmModal.type === 'browser-config'
        ? await settingsService.deleteBrowserConfig(confirmModal.item.id)
        : await settingsService.deleteSecretValue(confirmModal.item.id);

      if (!result.success) {
        setConfirmModal(prev => ({ ...prev, error: result.error || 'Failed to delete item', loading: false }));
        return;
      }

      // Refresh the list
      if (confirmModal.type === 'browser-config') {
        await fetchBrowserConfigs();
      } else {
        await fetchSecretValues();
      }
      
      // Close modal on success
      setConfirmModal({
        isOpen: false,
        type: 'browser-config',
        item: null,
        loading: false,
        error: null,
      });
    } catch (err) {
      setConfirmModal(prev => ({ ...prev, error: 'Failed to delete item', loading: false }));
      console.error('Error deleting item:', err);
    }
  };

  const toggleSecretVisibility = (secretId: string) => {
    setShowSecrets(prev => ({
      ...prev,
      [secretId]: !prev[secretId]
    }));
  };

  const handleEditProject = () => {
    setIsEditingProject(true);
  };

  const handleCancelEditProject = () => {
    setIsEditingProject(false);
    if (selectedProject) {
      setEditingProject({
        name: selectedProject.name,
        default_start_url: selectedProject.default_start_url,
      });
    }
  };

  const handleSaveProject = async () => {
    if (!selectedProject?.id) return;

    setProjectUpdateLoading(true);

    try {
      const updateData: UpdateProjectData = {};
      
      // Only include fields that have changed
      if (editingProject.name !== selectedProject.name) {
        updateData.name = editingProject.name;
      }
      if (editingProject.default_start_url !== selectedProject.default_start_url) {
        updateData.default_start_url = editingProject.default_start_url;
      }

      // If nothing changed, just exit edit mode
      if (Object.keys(updateData).length === 0) {
        setIsEditingProject(false);
        return;
      }

      const result = await settingsService.updateProject(selectedProject.id, updateData);

      if (!result.success) {
        console.error('Failed to update project:', result.error);
        return;
      }

      // Refresh projects to get updated data
      await refetchProjects();
      setIsEditingProject(false);
    } catch (err) {
      console.error('Error updating project:', err);
    } finally {
      setProjectUpdateLoading(false);
    }
  };

  const handleDeleteProject = () => {
    setShowProjectDeleteModal(true);
    setProjectDeleteError(null);
  };

  const confirmDeleteProject = async () => {
    if (!selectedProject?.id) return;
    
    try {
      setProjectDeleteLoading(true);
      setProjectDeleteError(null);
      
      await ProjectService.deleteProject(selectedProject.id);
      
      // Navigate back to home/project selection after successful deletion
      navigate('/');
    } catch (error: any) {
      console.error('Failed to delete project:', error);
      setProjectDeleteError(error.message || 'Failed to delete project');
    } finally {
      setProjectDeleteLoading(false);
    }
  };

  const cancelDeleteProject = () => {
    setShowProjectDeleteModal(false);
    setProjectDeleteError(null);
  };

  const formatBrowserConfig = (browserConfig: BrowserConfig) => {
    const config = browserConfig.browser_config;
    if (!config) return 'Default configuration';
    
    const parts = [];
    if (config.browser_channel) parts.push(config.browser_channel);
    if (config.viewport) parts.push(`${config.viewport.width}x${config.viewport.height}`);
    return parts.join(', ') || 'Default configuration';
  };

  const navigation = [
    { id: 'project', name: 'Project Settings', icon: SettingsIcon, description: 'Change project name and default URL' },
    { id: 'browser-configs', name: 'Browser Configurations', icon: Monitor, description: 'View and manage browser configs' },
    { id: 'secret-values', name: 'Secret Values', icon: Key, description: 'View and manage project secrets' },
    { id: 'global', name: 'Global Settings', icon: Globe, description: 'Application-wide settings', disabled: true },
    { id: 'integrations', name: 'Integrations (mock)', icon: SettingsIcon, description: 'Third-party integrations', disabled: true },
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'project':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Project Settings</h2>
                <p className="text-gray-600">Update your project name and default URL</p>
              </div>
              {!isEditingProject && (
                <button
                  onClick={handleEditProject}
                  className="p-2 text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                  title="Edit project settings"
                >
                  <Edit className="w-5 h-5" />
                </button>
              )}
            </div>
            
            <div className="bg-white p-6 rounded-lg border border-gray-200 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Project Name
                </label>
                <input
                  type="text"
                  value={isEditingProject ? editingProject.name : selectedProject?.name || ''}
                  onChange={(e) => isEditingProject && setEditingProject(prev => ({ ...prev, name: e.target.value }))}
                  readOnly={!isEditingProject}
                  className={`w-full px-3 py-2 border rounded-lg ${
                    isEditingProject 
                      ? 'border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500' 
                      : 'border-gray-300 bg-gray-50 text-gray-500 cursor-not-allowed'
                  }`}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Default Start URL
                </label>
                <input
                  type="url"
                  value={isEditingProject ? editingProject.default_start_url : selectedProject?.default_start_url || ''}
                  onChange={(e) => isEditingProject && setEditingProject(prev => ({ ...prev, default_start_url: e.target.value }))}
                  readOnly={!isEditingProject}
                  className={`w-full px-3 py-2 border rounded-lg ${
                    isEditingProject 
                      ? 'border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500' 
                      : 'border-gray-300 bg-gray-50 text-gray-500 cursor-not-allowed'
                  }`}
                />
              </div>
              
              {isEditingProject ? (
                <div className="flex items-center space-x-3">
                  <button
                    onClick={handleSaveProject}
                    disabled={projectUpdateLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-lg hover:bg-indigo-700 focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {projectUpdateLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                    <Save className="w-4 h-4" />
                    <span>{projectUpdateLoading ? 'Saving...' : 'Save Changes'}</span>
                  </button>
                  <button
                    onClick={handleCancelEditProject}
                    disabled={projectUpdateLoading}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    <XIcon className="w-4 h-4" />
                    <span>Cancel</span>
                  </button>
                </div>
              ) : (
                <div className="text-sm text-gray-500">
                  Click the edit icon to modify project settings
                </div>
              )}
            </div>

            {/* Danger Zone */}
            <div className="bg-white p-6 rounded-lg border border-red-200">
              <div className="flex items-start justify-between">
                <div className="flex-1 mr-6">
                  <h3 className="text-lg font-semibold text-red-800 mb-2">Danger Zone</h3>
                  <p className="text-gray-600">Permanently delete this project and all associated data.</p>
                </div>
                <button
                  onClick={handleDeleteProject}
                  disabled={isEditingProject}
                  className="flex-shrink-0 inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Project
                </button>
              </div>
            </div>
          </div>
        );

      case 'browser-configs':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Browser Configurations</h2>
                <p className="text-gray-600">Manage browser configurations for your test cases</p>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                <span className="ml-2 text-gray-600">Loading browser configurations...</span>
              </div>
            ) : browserConfigs.length === 0 ? (
              <div className="text-center py-12">
                <Monitor className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Browser Configurations</h3>
                <p className="text-gray-600">Create test cases to automatically generate browser configurations.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {browserConfigs.map((config) => (
                  <div key={config.id} className="bg-white p-4 rounded-lg border border-gray-200 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Monitor className="w-5 h-5 text-gray-500" />
                      <div>
                        <h3 className="font-medium text-gray-900">{formatBrowserConfig(config)}</h3>
                        <p className="text-sm text-gray-600">Created {new Date(config.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeleteBrowserConfig(config)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete browser configuration"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 'secret-values':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Secret Values</h2>
                <p className="text-gray-600">Manage secret values used in your test cases</p>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                <span className="ml-2 text-gray-600">Loading secret values...</span>
              </div>
            ) : secretValues.length === 0 ? (
              <div className="text-center py-12">
                <Key className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Secret Values</h3>
                <p className="text-gray-600">Create test cases with secrets to see them listed here.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {secretValues.map((secret) => (
                  <div key={secret.id} className="bg-white p-4 rounded-lg border border-gray-200 flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1">
                      <Key className="w-5 h-5 text-gray-500" />
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900 truncate">{secret.secret_name}</h3>
                        <div className="flex items-start space-x-2">
                          <p className={`text-sm text-gray-600 font-mono flex-1 ${
                            showSecrets[secret.id] ? 'break-all' : 'truncate'
                          }`}>
                            {showSecrets[secret.id] 
                              ? secret.secret_value 
                              : '•'.repeat(Math.min(secret.secret_value.length, 16))
                            }
                          </p>
                          <button
                            onClick={() => toggleSecretVisibility(secret.id)}
                            className="p-1 text-gray-500 hover:text-gray-700 transition-colors flex-shrink-0 mt-0.5"
                            title={showSecrets[secret.id] ? 'Hide secret' : 'Show secret'}
                          >
                            {showSecrets[secret.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                        <p className="text-xs text-gray-500">Created {new Date(secret.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeleteSecretValue(secret)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors ml-2"
                      title="Delete secret value"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      default:
        return (
          <div className="text-center py-12">
            <SettingsIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Coming Soon</h3>
            <p className="text-gray-600">This section is under development.</p>
          </div>
        );
    }
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">Manage settings for {selectedProject?.name || 'your project'}</p>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => !item.disabled && setActiveSection(item.id as SettingsSection)}
                disabled={item.disabled}
                className={`w-full text-left p-3 rounded-lg transition-colors flex items-start space-x-3 ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                    : item.disabled
                    ? 'text-gray-400 cursor-not-allowed'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
                  isActive ? 'text-indigo-600' : item.disabled ? 'text-gray-400' : 'text-gray-500'
                }`} />
                <div className="min-w-0">
                  <div className="font-medium">{item.name}</div>
                  <div className="text-sm text-gray-500 mt-1">{item.description}</div>
                </div>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-8 overflow-y-auto">
        {renderContent()}
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal(prev => ({ ...prev, isOpen: false, error: null }))}
        onConfirm={confirmDelete}
        type={confirmModal.type}
        itemName={
          confirmModal.type === 'browser-config'
            ? (confirmModal.item as BrowserConfig)?.browser_config 
              ? formatBrowserConfig(confirmModal.item as BrowserConfig)
              : 'Default configuration'
            : (confirmModal.item as SecretValue)?.secret_name || ''
        }
        loading={confirmModal.loading}
        error={confirmModal.error}
      />

      {/* Project Delete Confirmation Modal */}
      {showProjectDeleteModal && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-[10000]"
            onClick={cancelDeleteProject}
          />

          {/* Modal */}
          <div className="fixed inset-0 flex items-center justify-center z-[10001] p-4">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                    <Trash2 className="w-5 h-5 text-red-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">Delete Project</h2>
                    <p className="text-sm text-gray-500">This action cannot be undone</p>
                  </div>
                </div>
                <button
                  onClick={cancelDeleteProject}
                  disabled={projectDeleteLoading}
                  className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <XIcon className="w-4 h-4 text-gray-500" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 space-y-4">
                {projectDeleteError && (
                  <div className="flex items-center p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
                    <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                    <span>{projectDeleteError}</span>
                  </div>
                )}

                <div className="flex items-center p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <Globe className="w-5 h-5 text-red-600 mr-3" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-700 truncate">{selectedProject?.name}</p>
                    <p className="text-sm text-gray-500 truncate">{selectedProject?.default_start_url}</p>
                  </div>
                </div>

                <div className="space-y-2 text-sm text-gray-600">
                  <p className="font-medium text-red-800">This will permanently delete:</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>The entire project and its configuration</li>
                    <li>All test cases and their configurations</li>
                    <li>All test runs and execution history</li>
                    <li>All browser configurations</li>
                    <li>All secret values</li>
                    <li>All documents and traversals</li>
                  </ul>
                </div>

                <p className="text-sm text-gray-600 font-medium">
                  Are you absolutely sure you want to delete this project?
                </p>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={cancelDeleteProject}
                  disabled={projectDeleteLoading}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={confirmDeleteProject}
                  disabled={projectDeleteLoading}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {projectDeleteLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                  <span>{projectDeleteLoading ? 'Deleting...' : 'Delete Project'}</span>
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Settings;