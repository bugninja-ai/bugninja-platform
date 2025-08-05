import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Globe,
  Eye,
  EyeOff,
  Copy,
  CheckCircle,
  Clock,
  Calendar,
  Target,
  Monitor,
  MapPin,
  AlertCircle,
  Edit,
  Save,
  X,
  Plus,
  Trash2,
  History,
  Play,
  PlaySquare,
  User,
  Computer,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { FrontendTestCase, TestCategory, TestPriority } from '../types';
import { TestCaseService } from '../services/testCaseService';
import { BrowserService, BrowserConfigOptions, BrowserConfigData, UpdateBrowserConfigWithId, CreateBrowserConfigRequest } from '../services/browserService';
import { CustomDropdown } from '../components/CustomDropdown';
import { BASE_DOMAIN } from '../services/api';

const TestCaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [testCase, setTestCase] = useState<FrontendTestCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [visibleSecrets, setVisibleSecrets] = useState<Set<string>>(new Set());
  const [copiedSecret, setCopiedSecret] = useState<string | null>(null);
  const [recentTestRuns, setRecentTestRuns] = useState<any[]>([]);
  const [testRunsLoading, setTestRunsLoading] = useState(false);
  
  // Edit mode states
  const [editingConfig, setEditingConfig] = useState(false);
  const [editingRules, setEditingRules] = useState(false);
  const [editingBrowsers, setEditingBrowsers] = useState(false);
  const [editingSecrets, setEditingSecrets] = useState(false);
  const [editingGoal, setEditingGoal] = useState(false);
  const [editingBasicInfo, setEditingBasicInfo] = useState(false);
  
  // Browser config data and dropdown states
  const [browserConfigOptions, setBrowserConfigOptions] = useState<BrowserConfigOptions | null>(null);
  const [existingBrowserConfigs, setExistingBrowserConfigs] = useState<BrowserConfigData[]>([]);
  const [existingBrowserConfigDropdownOpen, setExistingBrowserConfigDropdownOpen] = useState(false);
  const [browserChannelDropdowns, setBrowserChannelDropdowns] = useState<Record<string, boolean>>({});
  const [userAgentDropdowns, setUserAgentDropdowns] = useState<Record<string, boolean>>({});
  const [viewportDropdowns, setViewportDropdowns] = useState<Record<string, boolean>>({});
  const [categoryDropdownOpen, setCategoryDropdownOpen] = useState(false);
  const [priorityDropdownOpen, setPriorityDropdownOpen] = useState(false);
  
  // Editable values
  const [editableTestCase, setEditableTestCase] = useState<FrontendTestCase | null>(null);

  useEffect(() => {
    if (id) {
      loadTestCase(id);
    }
  }, [id]);

  useEffect(() => {
    loadBrowserConfigOptions();
  }, []);

  const loadBrowserConfigOptions = async () => {
    try {
      const options = await BrowserService.getBrowserConfigOptions();
      setBrowserConfigOptions(options);
    } catch (error) {
      console.error('Failed to load browser config options:', error);
    }
  };

  const loadExistingBrowserConfigs = async (projectId: string) => {
    try {
      const browserConfigsData = await BrowserService.getBrowserConfigsByProject(projectId);
      setExistingBrowserConfigs(browserConfigsData);
    } catch (error) {
      console.error('Failed to load existing browser configs:', error);
      setExistingBrowserConfigs([]);
    }
  };

  // Category options for dropdown
  const categoryOptions = [
    { value: 'authentication', label: 'Authentication' },
    { value: 'banking', label: 'Banking' },
    { value: 'payments', label: 'Payments' },
    { value: 'security', label: 'Security' },
    { value: 'ui', label: 'UI' },
    { value: 'api', label: 'API' }
  ];

  // Priority options for dropdown
  const priorityOptions = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' },
  ];

  const loadTestCase = async (testCaseId: string) => {
    try {
      setLoading(true);
      setError(null);
      const tc = await TestCaseService.getTestCase(testCaseId);
      setTestCase(tc);
      setEditableTestCase(tc);
      
      // Load recent test runs and existing browser configs in parallel
      loadRecentTestRuns(testCaseId);
      loadExistingBrowserConfigs(tc.projectId);
    } catch (error: any) {
      console.error('Failed to load test case:', error);
      setError(error.message || 'Failed to load test case');
    } finally {
      setLoading(false);
    }
  };

  const loadRecentTestRuns = async (testCaseId: string) => {
    try {
      setTestRunsLoading(true);
      const runs = await TestCaseService.getRecentTestRuns(testCaseId, 3);
      setRecentTestRuns(runs);
    } catch (error: any) {
      console.error('Failed to load recent test runs:', error);
      // Don't set error state for test runs, just log and continue
    } finally {
      setTestRunsLoading(false);
    }
  };

  // Edit handlers
  const handleEditConfig = () => {
    setEditingConfig(true);
    setEditableTestCase({ ...testCase! });
  };

  const handleSaveConfig = async () => {
    if (!editableTestCase) return;
    try {
      // Here you would normally call an API to save the changes
      // await mockApi.updateTestCase(editableTestCase);
      setTestCase(editableTestCase);
      setEditingConfig(false);
    } catch (error) {
      console.error('Failed to save test case:', error);
    }
  };

  const handleCancelConfig = () => {
    setEditableTestCase({ ...testCase! });
    setEditingConfig(false);
  };

  const handleEditGoal = () => {
    setEditingGoal(true);
    setEditableTestCase({ ...testCase! });
  };

  const handleSaveGoal = async () => {
    if (!editableTestCase) return;
    try {
      // Here you would normally call an API to save the changes
      // await mockApi.updateTestCase(editableTestCase);
      setTestCase(editableTestCase);
      setEditingGoal(false);
    } catch (error) {
      console.error('Failed to save test case goal:', error);
    }
  };

  const handleCancelGoal = () => {
    setEditableTestCase({ ...testCase! });
    setEditingGoal(false);
  };

  const handleEditBasicInfo = () => {
    setEditingBasicInfo(true);
    setEditableTestCase({ ...testCase! });
  };

  const handleSaveBasicInfo = async () => {
    if (!editableTestCase) return;
    try {
      // Here you would normally call an API to save the changes
      // await mockApi.updateTestCase(editableTestCase);
      setTestCase(editableTestCase);
      setEditingBasicInfo(false);
      setCategoryDropdownOpen(false);
      setPriorityDropdownOpen(false);
    } catch (error) {
      console.error('Failed to save basic information:', error);
    }
  };

  const handleCancelBasicInfo = () => {
    setEditableTestCase({ ...testCase! });
    setEditingBasicInfo(false);
    setCategoryDropdownOpen(false);
    setPriorityDropdownOpen(false);
  };

  const handleEditRules = () => {
    setEditingRules(true);
    setEditableTestCase({ ...testCase! });
  };

  const handleSaveRules = async () => {
    if (!editableTestCase) return;
    try {
      setTestCase(editableTestCase);
      setEditingRules(false);
    } catch (error) {
      console.error('Failed to save extra rules:', error);
    }
  };

  const handleCancelRules = () => {
    setEditableTestCase({ ...testCase! });
    setEditingRules(false);
  };

  const handleEditBrowsers = () => {
    setEditingBrowsers(true);
    setEditableTestCase({ ...testCase! });
  };

  const handleSaveBrowsers = async () => {
    if (!editableTestCase || !testCase) return;
    try {
      // Separate existing configs (to update) from new configs (to create)
      const existingConfigs: UpdateBrowserConfigWithId[] = [];
      const newConfigs: CreateBrowserConfigRequest[] = [];
      const configsToUnlink: string[] = [];

      // Get the original browser configs to compare
      const originalConfigIds = new Set(testCase.browserConfigs.map(c => c.id));
      const currentConfigIds = new Set(editableTestCase.browserConfigs.map(c => c.id));

      // Find configs that were removed (to unlink)
      originalConfigIds.forEach(id => {
        if (!currentConfigIds.has(id)) {
          configsToUnlink.push(id);
        }
      });

      // Process current configs
      editableTestCase.browserConfigs.forEach(config => {
        if (config.id.startsWith('config-')) {
          // This is a new config (temporary ID)
          newConfigs.push({
            test_case_id: testCase.id,
            browser_config: {
              browser_channel: config.browserChannel,
              user_agent: config.userAgent,
              viewport: {
                width: config.viewport.width,
                height: config.viewport.height
              },
              geolocation: config.geolocation
            }
          });
        } else {
          // This is an existing config to update
          existingConfigs.push({
            id: config.id,
            browser_config: {
              browser_channel: config.browserChannel,
              user_agent: config.userAgent,
              viewport: {
                width: config.viewport.width,
                height: config.viewport.height
              },
              geolocation: config.geolocation
            }
          });
        }
      });

      // Get existing browser config IDs to link (if any)
      const existingBrowserConfigIdsToAdd = editableTestCase.existingBrowserConfigIds || [];

      // Call the bulk update API with all operations
      const response = await BrowserService.bulkUpdateBrowserConfigs({
        browser_configs: existingConfigs,
        new_browser_configs: newConfigs,
        existing_browser_config_ids_to_add: existingBrowserConfigIdsToAdd,
        browser_config_ids_to_unlink: configsToUnlink,
        test_case_id: testCase.id
      });
      
      console.log('Browser configs operations completed:', response);
      
      // Combine updated, created, and linked configs for the UI
      const allUpdatedConfigs = [
        ...response.updated_browser_configs,
        ...response.created_browser_configs,
        ...response.linked_browser_configs
      ].map(backendConfig => ({
        id: backendConfig.id,
        browserChannel: backendConfig.browser_config.browser_channel || '',
        userAgent: backendConfig.browser_config.user_agent || '',
        viewport: backendConfig.browser_config.viewport || { width: 1920, height: 1080 },
        geolocation: backendConfig.browser_config.geolocation
      }));

      // Update the test case state
      const updatedTestCase = {
        ...editableTestCase,
        browserConfigs: allUpdatedConfigs,
        existingBrowserConfigIds: [] // Clear the linked IDs after saving
      };

      setTestCase(updatedTestCase);
      setEditingBrowsers(false);
      
      // Reset dropdown states
      setBrowserChannelDropdowns({});
      setUserAgentDropdowns({});
      setViewportDropdowns({});
      setExistingBrowserConfigDropdownOpen(false);
      
    } catch (error: any) {
      console.error('Failed to save browser configurations:', error);
      
      // Show error to user - you could implement a toast notification here
      alert(`Failed to save browser configurations: ${error.message || 'Unknown error'}`);
    }
  };

  const handleCancelBrowsers = () => {
    setEditableTestCase({ ...testCase! });
    setEditingBrowsers(false);
    // Reset dropdown states
    setBrowserChannelDropdowns({});
    setUserAgentDropdowns({});
    setViewportDropdowns({});
    setExistingBrowserConfigDropdownOpen(false);
  };

  const handleEditSecrets = () => {
    setEditingSecrets(true);
    setEditableTestCase({ ...testCase! });
  };

  const handleSaveSecrets = async () => {
    if (!editableTestCase) return;
    try {
      setTestCase(editableTestCase);
      setEditingSecrets(false);
    } catch (error) {
      console.error('Failed to save secrets:', error);
    }
  };

  const handleCancelSecrets = () => {
    setEditableTestCase({ ...testCase! });
    setEditingSecrets(false);
  };

  const toggleSecretVisibility = (secretId: string) => {
    const newVisibleSecrets = new Set(visibleSecrets);
    if (newVisibleSecrets.has(secretId)) {
      newVisibleSecrets.delete(secretId);
    } else {
      newVisibleSecrets.add(secretId);
    }
    setVisibleSecrets(newVisibleSecrets);
  };

  const copySecret = async (value: string, secretId: string) => {
    try {
      await navigator.clipboard.writeText(value);
      setCopiedSecret(secretId);
      setTimeout(() => setCopiedSecret(null), 2000);
    } catch (error) {
      console.error('Failed to copy secret:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'passed':
      case 'finished':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'pending':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    const normalizedStatus = status.toLowerCase();
    switch (normalizedStatus) {
      case 'passed':
      case 'finished':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'failed':
        return <X className="w-4 h-4 text-red-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-amber-500" />;
      default:
        return <Clock className="w-4 h-4 text-amber-500" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading test case details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-800 mb-2">Failed to load test case</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-x-3">
            <button
              onClick={() => id && loadTestCase(id)}
              className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Try again
            </button>
            <Link
              to="/"
              className="inline-flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Back to test cases
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!testCase) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-800 mb-2">Test case not found</h3>
          <p className="text-gray-600 mb-4">The requested test case could not be found.</p>
          <Link
            to="/"
            className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Back to test cases
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h1 className="text-3xl font-bold text-gray-800">{testCase.title}</h1>
            <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-lg">{testCase.code}</span>
            <span className={`inline-flex items-center text-xs font-semibold px-2.5 py-1 rounded-full border ${getPriorityColor(testCase.priority)}`}>
              {testCase.priority.charAt(0).toUpperCase() + testCase.priority.slice(1)}
            </span>
            <span className={`inline-flex items-center space-x-1 text-xs font-semibold px-2.5 py-1 rounded-full border ${getStatusColor(testCase.status)}`}>
              {getStatusIcon(testCase.status)}
              <span>{testCase.status.charAt(0).toUpperCase() + testCase.status.slice(1)}</span>
            </span>
          </div>
          <p className="text-gray-600 mb-4">{testCase.description}</p>
        </div>

        <Link
          to="/"
          className="inline-flex items-center px-3 py-2 text-sm font-medium border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to test cases
        </Link>
      </div>

      {/* Test Goal */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200 mt-8 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Target className="h-5 w-5 text-blue-600" />
            <span className="text-lg font-semibold text-gray-800">Test goal</span>
          </div>
          <div className="flex items-center space-x-2">
            {editingGoal ? (
              <>
                <button
                  onClick={handleSaveGoal}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Save className="w-4 h-4 mr-1" />
                  Save
                </button>
                <button
                  onClick={handleCancelGoal}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <X className="w-4 h-4 mr-1" />
                  Cancel
                </button>
              </>
            ) : (
              <button
                onClick={handleEditGoal}
                className="inline-flex items-center p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                title="Edit goal"
              >
                <Edit className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
        {editingGoal ? (
          <textarea
            value={editableTestCase?.goal || ''}
            onChange={(e) => setEditableTestCase(prev => prev ? { ...prev, goal: e.target.value } : null)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
            placeholder="Enter test goal"
            rows={3}
          />
        ) : (
          <p className="text-gray-600">{testCase.goal}</p>
        )}
      </div>

      {/* Basic Information */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200" style={{ position: 'relative', zIndex: editingBasicInfo && (categoryDropdownOpen || priorityDropdownOpen) ? 1000 : 'auto' }}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Basic information</h2>
          <div className="flex items-center space-x-2">
            {editingBasicInfo ? (
              <>
                <button
                  onClick={handleSaveBasicInfo}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Save className="w-4 h-4 mr-1" />
                  Save
                </button>
                <button
                  onClick={handleCancelBasicInfo}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <X className="w-4 h-4 mr-1" />
                  Cancel
                </button>
              </>
            ) : (
              <button
                onClick={handleEditBasicInfo}
                className="inline-flex items-center p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                title="Edit basic information"
              >
                <Edit className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Test case ID</label>
            <div className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
              {testCase.id}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Project ID</label>
            <div className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
              {testCase.projectId}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            {editingBasicInfo ? (
              <CustomDropdown
                options={categoryOptions}
                value={editableTestCase?.category || ''}
                onChange={(value) => setEditableTestCase(prev => prev ? { ...prev, category: value as TestCategory } : null)}
                isOpen={categoryDropdownOpen}
                setIsOpen={setCategoryDropdownOpen}
                placeholder="Select Category"
                fullWidth={true}
              />
            ) : (
              <div className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800 capitalize">
                {testCase.category}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
            {editingBasicInfo ? (
              <CustomDropdown
                options={priorityOptions}
                value={editableTestCase?.priority || ''}
                onChange={(value) => setEditableTestCase(prev => prev ? { ...prev, priority: value as TestPriority } : null)}
                isOpen={priorityDropdownOpen}
                setIsOpen={setPriorityDropdownOpen}
                placeholder="Select Priority"
                fullWidth={true}
              />
            ) : (
              <div className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800 capitalize">
                {testCase.priority}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Created</label>
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span>{testCase.createdAt.toLocaleDateString()}</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Last updated</label>
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span>{testCase.updatedAt.toLocaleDateString()}</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Total runs</label>
            <div className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
              {testCase.totalRuns}
            </div>
          </div>
        </div>
      </div>

      {/* Test Configuration */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Test configuration</h2>
          <div className="flex items-center space-x-2">
            {editingConfig ? (
              <>
                <button
                  onClick={handleSaveConfig}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Save className="w-4 h-4 mr-1" />
                  Save
                </button>
                <button
                  onClick={handleCancelConfig}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <X className="w-4 h-4 mr-1" />
                  Cancel
                </button>
              </>
            ) : (
              <button
                onClick={handleEditConfig}
                className="inline-flex items-center p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                title="Edit configuration"
              >
                <Edit className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
        
        <div className="space-y-6">
          {/* Starting URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Starting URL</label>
            {editingConfig ? (
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-gray-400 ml-3" />
                <input
                  type="url"
                  value={editableTestCase?.startingUrl || ''}
                  onChange={(e) => setEditableTestCase(prev => prev ? { ...prev, startingUrl: e.target.value } : null)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter starting URL"
                />
              </div>
            ) : (
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
              <Globe className="w-4 h-4 text-gray-400" />
              <span className="break-all">{testCase.startingUrl}</span>
            </div>
            )}
          </div>

          {/* Allowed Domains */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">Allowed domains</label>
              {editingConfig && (
                                  <button
                    onClick={() => {
                      if (editableTestCase) {
                        setEditableTestCase({
                          ...editableTestCase,
                          allowedDomains: [...editableTestCase.allowedDomains, '']
                        });
                      }
                    }}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add domain
                  </button>
              )}
            </div>
            <div className="space-y-2">
              {editingConfig ? (
                editableTestCase?.allowedDomains.map((domain, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Globe className="w-4 h-4 text-gray-400 ml-3" />
                    <input
                      type="text"
                      value={domain}
                      onChange={(e) => {
                        if (editableTestCase) {
                          const newDomains = [...editableTestCase.allowedDomains];
                          newDomains[index] = e.target.value;
                          setEditableTestCase({
                            ...editableTestCase,
                            allowedDomains: newDomains
                          });
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Enter domain"
                    />
                    <button
                      onClick={() => {
                        if (editableTestCase) {
                          const newDomains = editableTestCase.allowedDomains.filter((_, i) => i !== index);
                          setEditableTestCase({
                            ...editableTestCase,
                            allowedDomains: newDomains
                          });
                        }
                      }}
                      className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))
              ) : (
                testCase.allowedDomains.map((domain, index) => (
                <div key={index} className="flex items-center space-x-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
                  <Globe className="w-4 h-4 text-gray-400" />
                  <span>{domain}</span>
                </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Extra Rules */}
      {(testCase.extraRules.length > 0 || editingRules) && (
        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-800">Extra rules</h2>
            <div className="flex items-center space-x-2">
              {editingRules ? (
                <>
                  <button
                    onClick={() => {
                      if (editableTestCase) {
                        const newRule = {
                          id: `rule-${Date.now()}`,
                          ruleNumber: editableTestCase.extraRules.length + 1,
                          description: ''
                        };
                        setEditableTestCase({
                          ...editableTestCase,
                          extraRules: [...editableTestCase.extraRules, newRule]
                        });
                      }
                    }}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add rule
                  </button>
                  <button
                    onClick={handleSaveRules}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Save className="w-4 h-4 mr-1" />
                    Save
                  </button>
                  <button
                    onClick={handleCancelRules}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <X className="w-4 h-4 mr-1" />
                    Cancel
                  </button>
                </>
              ) : (
                <button
                  onClick={handleEditRules}
                  className="inline-flex items-center p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Edit extra rules"
                >
                  <Edit className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
          
          <div className="space-y-3">
            {editingRules ? (
              editableTestCase?.extraRules.map((rule, index) => (
                <div key={rule.id} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-sm font-medium text-indigo-600 mt-1">
                    {rule.ruleNumber}
                  </div>
                  <div className="flex-1">
                    <textarea
                      value={rule.description}
                      onChange={(e) => {
                        if (editableTestCase) {
                          const newRules = [...editableTestCase.extraRules];
                          newRules[index] = { ...newRules[index], description: e.target.value };
                          setEditableTestCase({
                            ...editableTestCase,
                            extraRules: newRules
                          });
                        }
                      }}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                      rows={2}
                      placeholder="Enter rule description"
                    />
                  </div>
                  <button
                    onClick={() => {
                      if (editableTestCase) {
                        const newRules = editableTestCase.extraRules.filter((_, i) => i !== index);
                        // Renumber remaining rules
                        const renumberedRules = newRules.map((r, i) => ({ ...r, ruleNumber: i + 1 }));
                        setEditableTestCase({
                          ...editableTestCase,
                          extraRules: renumberedRules
                        });
                      }
                    }}
                    className="flex-shrink-0 p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors mt-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            ) : (
              testCase.extraRules.map((rule) => (
              <div key={rule.id} className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-sm font-medium text-indigo-600 mt-1">
                  {rule.ruleNumber}
                </div>
                <div className="flex-1">
                  <div className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
                    {rule.description}
                  </div>
                </div>
              </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Browser Configurations */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Browser configurations</h2>
          <div className="flex items-center space-x-2">
            {editingBrowsers ? (
              <>
                <button
                  onClick={() => {
                    if (editableTestCase) {
                      const newConfig = {
                        id: `config-${Date.now()}`,
                        browserChannel: '',
                        userAgent: '',
                        viewport: { width: 1920, height: 1080 },
                        geolocation: undefined
                      };
                      setEditableTestCase({
                        ...editableTestCase,
                        browserConfigs: [...editableTestCase.browserConfigs, newConfig]
                      });
                    }
                  }}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add config
                </button>
                <button
                  onClick={handleSaveBrowsers}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Save className="w-4 h-4 mr-1" />
                  Save
                </button>
                <button
                  onClick={handleCancelBrowsers}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <X className="w-4 h-4 mr-1" />
                  Cancel
                </button>
              </>
            ) : (
              <button
                onClick={handleEditBrowsers}
                className="inline-flex items-center p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                title="Edit browser configurations"
              >
                <Edit className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Select Existing Browser Config - Only show in edit mode */}
        {editingBrowsers && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Or select an existing browser configuration
            </label>
            
            {existingBrowserConfigs.length === 0 ? (
              <div className="text-sm text-gray-500 italic">
                No existing browser configurations found for this project
              </div>
            ) : (
              <CustomDropdown
                options={existingBrowserConfigs
                  .filter(config => !editableTestCase?.browserConfigs.some(existing => existing.id === config.id))
                  .map(config => {
                    const viewport = config.browser_config?.viewport;
                    const userAgent = config.browser_config?.user_agent || '';
                    
                    // Extract browser type from user agent (same logic as CreateTest.tsx)
                    let browserType = 'Unknown';
                    if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) browserType = 'Chromium';
                    else if (userAgent.includes('Firefox')) browserType = 'Firefox';
                    else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) browserType = 'Webkit';
                    else if (userAgent.includes('Edg')) browserType = 'Microsoft Edge';
                    
                    return {
                      value: config.id,
                      label: `${browserType} - ${viewport?.width || 1920}×${viewport?.height || 1080}`
                    };
                  })}
                value=""
                onChange={(configId) => {
                  if (configId && editableTestCase) {
                    // Add the existing config ID to a special field for linking
                    if (!editableTestCase.existingBrowserConfigIds) {
                      editableTestCase.existingBrowserConfigIds = [];
                    }
                    if (!editableTestCase.existingBrowserConfigIds.includes(configId)) {
                      setEditableTestCase({
                        ...editableTestCase,
                        existingBrowserConfigIds: [...editableTestCase.existingBrowserConfigIds, configId]
                      });
                    }
                  }
                }}
                isOpen={existingBrowserConfigDropdownOpen}
                setIsOpen={setExistingBrowserConfigDropdownOpen}
                placeholder="Select existing configuration"
                fullWidth={true}
              />
            )}
          </div>
        )}
        
        <div className="space-y-4">
          {editingBrowsers ? (
            editableTestCase?.browserConfigs.map((config, index) => (
              <div key={config.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Monitor className="w-5 h-5 text-gray-400" />
                    <span className="font-medium text-gray-800">Browser Configuration</span>
                  </div>
                  <button
                    onClick={() => {
                      if (editableTestCase) {
                        const newConfigs = editableTestCase.browserConfigs.filter((_, i) => i !== index);
                        setEditableTestCase({
                          ...editableTestCase,
                          browserConfigs: newConfigs
                        });
                      }
                    }}
                    className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm overflow-visible">
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Browser Channel</label>
                    <CustomDropdown
                      options={browserConfigOptions?.browser_channels.map(channel => ({ value: channel, label: channel })) || []}
                      value={config.browserChannel || ''}
                      onChange={(value) => {
                        if (editableTestCase) {
                          const newConfigs = [...editableTestCase.browserConfigs];
                          newConfigs[index] = { ...newConfigs[index], browserChannel: value };
                          setEditableTestCase({
                            ...editableTestCase,
                            browserConfigs: newConfigs
                          });
                        }
                      }}
                      isOpen={browserChannelDropdowns[config.id] || false}
                      setIsOpen={(open) => setBrowserChannelDropdowns(prev => ({ ...prev, [config.id]: open }))}
                      placeholder="Select Browser Channel"
                      fullWidth={true}
                    />
                  </div>
                  
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-500 mb-1">User Agent</label>
                    <CustomDropdown
                      options={browserConfigOptions?.user_agents.map(agent => ({ value: agent, label: agent.slice(0, 50) + '...' })) || []}
                      value={config.userAgent || ''}
                      onChange={(value) => {
                        if (editableTestCase) {
                          const newConfigs = [...editableTestCase.browserConfigs];
                          newConfigs[index] = { ...newConfigs[index], userAgent: value };
                          setEditableTestCase({
                            ...editableTestCase,
                            browserConfigs: newConfigs
                          });
                        }
                      }}
                      isOpen={userAgentDropdowns[config.id] || false}
                      setIsOpen={(open) => setUserAgentDropdowns(prev => ({ ...prev, [config.id]: open }))}
                      placeholder="Select User Agent"
                      fullWidth={true}
                    />
                  </div>
                  
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Viewport Size</label>
                    <CustomDropdown
                      options={browserConfigOptions?.viewport_sizes.map(viewport => ({
                        value: `${viewport.width}x${viewport.height}`,
                        label: `${viewport.width} × ${viewport.height}`
                      })) || []}
                      value={config.viewport ? `${config.viewport.width}x${config.viewport.height}` : ''}
                      onChange={(value) => {
                        if (editableTestCase) {
                          const [width, height] = value.split('x').map(Number);
                          const newConfigs = [...editableTestCase.browserConfigs];
                          newConfigs[index] = { 
                            ...newConfigs[index], 
                            viewport: { width, height }
                          };
                          setEditableTestCase({
                            ...editableTestCase,
                            browserConfigs: newConfigs
                          });
                        }
                      }}
                      isOpen={viewportDropdowns[config.id] || false}
                      setIsOpen={(open) => setViewportDropdowns(prev => ({ ...prev, [config.id]: open }))}
                      placeholder="Select Viewport Size"
                      fullWidth={true}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Latitude (optional)</label>
                    <input
                      type="number"
                      step="any"
                      value={config.geolocation?.latitude || ''}
                      onChange={(e) => {
                        if (editableTestCase) {
                          const newConfigs = [...editableTestCase.browserConfigs];
                          const value = e.target.value;
                          if (value) {
                            newConfigs[index] = {
                              ...newConfigs[index],
                              geolocation: {
                                latitude: parseFloat(value),
                                longitude: newConfigs[index].geolocation?.longitude || 0
                              }
                            };
                          } else {
                            newConfigs[index] = { ...newConfigs[index], geolocation: undefined };
                          }
                          setEditableTestCase({
                            ...editableTestCase,
                            browserConfigs: newConfigs
                          });
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
                      placeholder="e.g. 40.7128"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Longitude (optional)</label>
                    <input
                      type="number"
                      step="any"
                      value={config.geolocation?.longitude || ''}
                      onChange={(e) => {
                        if (editableTestCase) {
                          const newConfigs = [...editableTestCase.browserConfigs];
                          const value = e.target.value;
                          if (value) {
                            newConfigs[index] = {
                              ...newConfigs[index],
                              geolocation: {
                                latitude: newConfigs[index].geolocation?.latitude || 0,
                                longitude: parseFloat(value)
                              }
                            };
                          } else if (!config.geolocation?.latitude) {
                            newConfigs[index] = { ...newConfigs[index], geolocation: undefined };
                          }
                          setEditableTestCase({
                            ...editableTestCase,
                            browserConfigs: newConfigs
                          });
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
                      placeholder="e.g. -74.0060"
                    />
                  </div>
                </div>
              </div>
            ))
          ) : (
            testCase.browserConfigs.map((config) => (
            <div key={config.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Monitor className="w-5 h-5 text-gray-400" />
                <h3 className="font-medium text-gray-800">Browser Configuration</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Browser Channel</label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded text-gray-700">
                    {config.browserChannel || 'No browser channel specified'}
                  </div>
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Viewport</label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded text-gray-700">
                    {config.viewport ? `${config.viewport.width} × ${config.viewport.height}` : 'No viewport specified'}
                  </div>
                </div>
                
                {config.geolocation && 
                 config.geolocation.latitude !== undefined && 
                 config.geolocation.longitude !== undefined && (
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Geolocation</label>
                    <div className="flex items-center space-x-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded text-gray-700">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span>{config.geolocation.latitude}, {config.geolocation.longitude}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
            ))
          )}
        </div>
      </div>

      {/* Secrets */}
      {(testCase.secrets.length > 0 || editingSecrets) && (
        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
            <h2 className="text-lg font-semibold text-gray-800">Secrets</h2>
            </div>
            <div className="flex items-center space-x-2">
              {editingSecrets ? (
                <>
                  <button
                    onClick={() => {
                      if (editableTestCase) {
                        const newSecret = {
                          id: `secret-${Date.now()}`,
                          secretName: '',
                          value: ''
                        };
                        setEditableTestCase({
                          ...editableTestCase,
                          secrets: [...editableTestCase.secrets, newSecret]
                        });
                      }
                    }}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add secret
                  </button>
                  <button
                    onClick={handleSaveSecrets}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Save className="w-4 h-4 mr-1" />
                    Save
                  </button>
                  <button
                    onClick={handleCancelSecrets}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <X className="w-4 h-4 mr-1" />
                    Cancel
                  </button>
                </>
              ) : (
                <button
                  onClick={handleEditSecrets}
                  className="inline-flex items-center p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Edit secrets"
                >
                  <Edit className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
          
          <div className="space-y-3">
            {editingSecrets ? (
              editableTestCase?.secrets.map((secret, index) => (
                <div key={secret.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <input
                      type="text"
                      value={secret.secretName}
                      onChange={(e) => {
                        if (editableTestCase) {
                          const newSecrets = [...editableTestCase.secrets];
                          newSecrets[index] = { ...newSecrets[index], secretName: e.target.value };
                          setEditableTestCase({
                            ...editableTestCase,
                            secrets: newSecrets
                          });
                        }
                      }}
                      className="text-sm font-medium text-gray-700 bg-transparent border-b border-gray-300 focus:border-indigo-500 focus:outline-none flex-1 mr-4"
                      placeholder="Secret name"
                    />
                    <button
                      onClick={() => {
                        if (editableTestCase) {
                          const newSecrets = editableTestCase.secrets.filter((_, i) => i !== index);
                          setEditableTestCase({
                            ...editableTestCase,
                            secrets: newSecrets
                          });
                        }
                      }}
                      className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <div className="relative">
                    <input
                      type="text"
                      value={secret.value}
                      onChange={(e) => {
                        if (editableTestCase) {
                          const newSecrets = [...editableTestCase.secrets];
                          newSecrets[index] = { ...newSecrets[index], value: e.target.value };
                          setEditableTestCase({
                            ...editableTestCase,
                            secrets: newSecrets
                          });
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-gray-800 font-mono text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Secret value"
                    />
                  </div>
                </div>
              ))
            ) : (
              testCase.secrets.map((secret) => (
              <div key={secret.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">{secret.secretName}</label>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleSecretVisibility(secret.id)}
                      className="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors"
                      title={visibleSecrets.has(secret.id) ? 'Hide value' : 'Show value'}
                    >
                      {visibleSecrets.has(secret.id) ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </button>
                    <button
                      onClick={() => copySecret(secret.value, secret.id)}
                      className="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors"
                      title="Copy to clipboard"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <div className="relative">
                  <input
                    type={visibleSecrets.has(secret.id) ? 'text' : 'password'}
                    value={secret.value}
                    readOnly
                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded text-gray-800 font-mono text-sm"
                  />
                  {copiedSecret === secret.id && (
                    <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-1 text-emerald-600 text-xs">
                      <CheckCircle className="w-3 h-3" />
                      <span>Copied!</span>
                    </div>
                  )}
                </div>
              </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Run History Summary */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Recent test runs</h2>
          <Link
            to={`/runs?testCase=${testCase.id}`}
            className="inline-flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
          >
            <History className="w-4 h-4 mr-1" />
            View all runs
          </Link>
        </div>
        
        <div className="space-y-4">
          {testRunsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-indigo-600 mr-2" />
              <span className="text-gray-600">Loading recent test runs...</span>
            </div>
          ) : recentTestRuns.length > 0 ? (
            recentTestRuns.map((run) => {
              const startedAt = new Date(run.started_at || run.startedAt || run.created_at);
              const completedAt = run.finished_at || run.completed_at || run.completedAt;
              const duration = run.duration || (completedAt ? (new Date(completedAt).getTime() - startedAt.getTime()) / 1000 : 0);
              const passedSteps = run.passed_steps || run.passedSteps || 0;
              const totalSteps = run.total_steps || run.totalSteps || run.steps?.length || 0;
              const status = (run.status || run.current_state || 'PENDING').toUpperCase();
              const runGifPath = run.run_gif || run.runGif;
              const runGif = runGifPath ? `${BASE_DOMAIN}/${runGifPath}` : null;
              const runType = run.run_type || run.runType;
              const origin = run.origin;
              const browserConfig = run.browser_config || run.browserConfig;


              
              return (
                <div key={run.id} className="relative group bg-white rounded-lg p-6 border border-gray-200">
                  <div className="flex items-start space-x-4">
                    {/* GIF Display */}
                    {runGif && (
                      <div className="flex-shrink-0">
                        <div className="relative overflow-hidden rounded-xl border-2 border-gray-200 group-hover:border-gray-300 transition-colors">
                          <img 
                            src={runGif} 
                            alt="Test run animation"
                            className="w-28 h-20 object-cover"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                            }}
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        </div>
                      </div>
                    )}
                    
                    <div className="flex-1 min-w-0">
                      {/* Header with Status Badge */}
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <span className={`inline-flex items-center space-x-1 text-xs font-semibold px-2.5 py-1 rounded-full border ${getStatusColor(status.toLowerCase())}`}>
                            {getStatusIcon(status.toLowerCase())}
                            <span>{status}</span>
                          </span>
                          
                          {totalSteps > 0 && (
                            <div className="flex items-center space-x-1 text-sm text-gray-600 bg-gray-50 px-2 py-1 rounded-lg">
                              <span className="font-medium">{passedSteps}</span>
                              <span className="text-gray-400">/</span>
                              <span>{totalSteps}</span>
                              <span className="text-xs text-gray-500 ml-1">steps</span>
                            </div>
                          )}
                        </div>
                        
                        <Link
                          to={`/runs/${run.id}`}
                          className="inline-flex items-center px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-all duration-200"
                        >
                          <Eye className="w-4 h-4 mr-1.5" />
                          View details
                        </Link>
                      </div>
                      
                      {/* Details Row */}
                      <div className="flex items-center flex-wrap gap-x-6 gap-y-2">
                        <div className="flex items-center space-x-2 text-sm">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600">{startedAt.toLocaleDateString()} {startedAt.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                        </div>
                        
                        {duration > 0 && (
                          <div className="flex items-center space-x-2 text-sm">
                            <Clock className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-600">{duration.toFixed(1)}s</span>
                          </div>
                        )}

                        {runType && (
                          <div className="flex items-center space-x-1.5 text-sm">
                            <PlaySquare className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-600">{runType}</span>
                          </div>
                        )}
                        
                        {origin && (
                          <div className="flex items-center space-x-1.5 text-sm">
                            {origin.toLowerCase().includes('user') ? (
                              <User className="w-4 h-4 text-gray-400" />
                            ) : (
                              <Computer className="w-4 h-4 text-gray-400" />
                            )}
                            <span className="text-gray-600">{origin}</span>
                          </div>
                        )}
                        
                        {browserConfig?.browser_config?.viewport && (
                          <div className="flex items-center space-x-1.5 text-sm">
                            <Monitor className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-600">{browserConfig.browser_config.viewport.width}×{browserConfig.browser_config.viewport.height}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          ) : null}
          
          {!testRunsLoading && recentTestRuns.length === 0 && (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">No test runs yet</h3>
              <p className="text-gray-600 mb-4">This test case hasn't been executed yet.</p>
              <Link
                to={`/runs/${testCase.id}/run`}
                className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <Play className="w-4 h-4 mr-2" />
                Run test now
              </Link>
            </div>
          )}
        </div>
      </div>
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Execution summary</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{testCase.totalRuns}</div>
            <div className="text-sm text-gray-600">Total Runs</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-emerald-600">{testCase.passedRuns}</div>
            <div className="text-sm text-gray-600">Passed</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{testCase.failedRuns}</div>
            <div className="text-sm text-gray-600">Failed</div>
          </div>
        </div>
        
        <div className="mt-4 bg-gray-200 rounded-full h-2">
          <div 
            className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${testCase.passRate}%` }}
          ></div>
        </div>
        <div className="text-center mt-2 text-sm text-gray-600">
          {testCase.passRate}% success rate
        </div>
      </div>
    </div>
  );
};

export default TestCaseDetail; 