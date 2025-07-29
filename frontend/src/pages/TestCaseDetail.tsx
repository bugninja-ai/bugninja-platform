import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  FileText,
  Globe,
  Settings,
  Eye,
  EyeOff,
  Copy,
  CheckCircle,
  Clock,
  Calendar,
  Target,
  Shield,
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
  Loader2,
  RefreshCw
} from 'lucide-react';
import { FrontendTestCase, TestCategory } from '../types';
import { TestCaseService } from '../services/testCaseService';
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
  
  // Dropdown states for browser configs
  const [userAgentDropdowns, setUserAgentDropdowns] = useState<Record<string, boolean>>({});
  const [viewportDropdowns, setViewportDropdowns] = useState<Record<string, boolean>>({});
  const [categoryDropdownOpen, setCategoryDropdownOpen] = useState(false);
  
  // Editable values
  const [editableTestCase, setEditableTestCase] = useState<FrontendTestCase | null>(null);

  useEffect(() => {
    if (id) {
      loadTestCase(id);
    }
  }, [id]);

  // Common user agents for dropdown
  const commonUserAgents = [
    { value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', label: 'Chrome (Windows)' },
    { value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', label: 'Chrome (macOS)' },
    { value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0', label: 'Firefox (Windows)' },
    { value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0', label: 'Firefox (macOS)' },
    { value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15', label: 'Safari (macOS)' },
    { value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0', label: 'Edge (Windows)' },
    { value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1', label: 'Safari (iPhone)' },
    { value: 'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1', label: 'Safari (iPad)' },
    { value: 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36', label: 'Chrome (Android)' },
    { value: 'custom', label: 'Custom User Agent' }
  ];

  // Common viewport resolutions for dropdown
  const commonViewports = [
    { value: '1920x1080', label: '1920 × 1080 (Full HD)' },
    { value: '1366x768', label: '1366 × 768 (HD)' },
    { value: '1440x900', label: '1440 × 900 (MacBook Air)' },
    { value: '1280x720', label: '1280 × 720 (HD)' },
    { value: '1024x768', label: '1024 × 768 (iPad)' },
    { value: '768x1024', label: '768 × 1024 (iPad Portrait)' },
    { value: '375x667', label: '375 × 667 (iPhone)' },
    { value: '414x896', label: '414 × 896 (iPhone Plus)' },
    { value: '360x640', label: '360 × 640 (Android)' },
    { value: 'custom', label: 'Custom Resolution' }
  ];

  // Category options for dropdown
  const categoryOptions = [
    { value: 'authentication', label: 'Authentication' },
    { value: 'banking', label: 'Banking' },
    { value: 'payments', label: 'Payments' },
    { value: 'security', label: 'Security' },
    { value: 'ui', label: 'UI' },
    { value: 'api', label: 'API' }
  ];

  const loadTestCase = async (testCaseId: string) => {
    try {
      setLoading(true);
      setError(null);
      const tc = await TestCaseService.getTestCase(testCaseId);
      setTestCase(tc);
      setEditableTestCase(tc);
      
      // Load recent test runs in parallel
      loadRecentTestRuns(testCaseId);
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
    } catch (error) {
      console.error('Failed to save basic information:', error);
    }
  };

  const handleCancelBasicInfo = () => {
    setEditableTestCase({ ...testCase! });
    setEditingBasicInfo(false);
    setCategoryDropdownOpen(false);
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
    if (!editableTestCase) return;
    try {
      setTestCase(editableTestCase);
      setEditingBrowsers(false);
      // Reset dropdown states
      setUserAgentDropdowns({});
      setViewportDropdowns({});
    } catch (error) {
      console.error('Failed to save browser configurations:', error);
    }
  };

  const handleCancelBrowsers = () => {
    setEditableTestCase({ ...testCase! });
    setEditingBrowsers(false);
    // Reset dropdown states
    setUserAgentDropdowns({});
    setViewportDropdowns({});
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

  const getStatusIcon = (status: string) => {
    const normalizedStatus = status.toLowerCase();
    switch (normalizedStatus) {
      case 'passed':
      case 'finished':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'failed':
        return <X className="w-4 h-4 text-red-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />;
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
              Try Again
            </button>
            <Link
              to="/"
              className="inline-flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Back to Test Cases
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
            Back to Test Cases
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
            <span className={`text-xs font-medium px-2 py-1 rounded-lg border ${getPriorityColor(testCase.priority)}`}>
              {testCase.priority}
            </span>
            <div className="flex items-center space-x-1">
              {getStatusIcon(testCase.status)}
              <span className={`text-sm font-medium ${
                testCase.status === 'passed' ? 'text-emerald-600' :
                testCase.status === 'failed' ? 'text-red-600' :
                'text-yellow-600'
              }`}>
                {testCase.status.charAt(0).toUpperCase() + testCase.status.slice(1)}
              </span>
            </div>
          </div>
          <p className="text-gray-600 mb-4">{testCase.description}</p>
        </div>

        <Link
          to="/"
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Test Cases
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
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Save className="w-4 h-4 mr-1" />
                  Save
                </button>
                <button
                  onClick={handleCancelGoal}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
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
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200" style={{ position: 'relative', zIndex: editingBasicInfo && categoryDropdownOpen ? 1000 : 'auto' }}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Basic information</h2>
          <div className="flex items-center space-x-2">
            {editingBasicInfo ? (
              <>
                <button
                  onClick={handleSaveBasicInfo}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Save className="w-4 h-4 mr-1" />
                  Save
                </button>
                <button
                  onClick={handleCancelBasicInfo}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
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
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Save className="w-4 h-4 mr-1" />
                  Save
                </button>
                <button
                  onClick={handleCancelConfig}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
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
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Domain
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
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Rule
                  </button>
                  <button
                    onClick={handleSaveRules}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Save className="w-4 h-4 mr-1" />
                    Save
                  </button>
                  <button
                    onClick={handleCancelRules}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
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
                        name: 'New Configuration',
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
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Config
                </button>
                <button
                  onClick={handleSaveBrowsers}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Save className="w-4 h-4 mr-1" />
                  Save
                </button>
                <button
                  onClick={handleCancelBrowsers}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
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
        
        <div className="space-y-4">
          {editingBrowsers ? (
            editableTestCase?.browserConfigs.map((config, index) => (
              <div key={config.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Monitor className="w-5 h-5 text-gray-600" />
                    <input
                      type="text"
                      value={config.name}
                      onChange={(e) => {
                        if (editableTestCase) {
                          const newConfigs = [...editableTestCase.browserConfigs];
                          newConfigs[index] = { ...newConfigs[index], name: e.target.value };
                          setEditableTestCase({
                            ...editableTestCase,
                            browserConfigs: newConfigs
                          });
                        }
                      }}
                      className="font-medium text-gray-800 bg-transparent border-b border-gray-300 focus:border-indigo-500 focus:outline-none"
                      placeholder="Configuration name"
                    />
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
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-500 mb-1">User agent</label>
                    <div className="space-y-2">
                      <CustomDropdown
                        options={commonUserAgents}
                        value={commonUserAgents.find(ua => ua.value === config.userAgent)?.value || 'custom'}
                        onChange={(value) => {
                          if (editableTestCase) {
                            const newConfigs = [...editableTestCase.browserConfigs];
                            if (value !== 'custom') {
                              newConfigs[index] = { ...newConfigs[index], userAgent: value };
                              setEditableTestCase({
                                ...editableTestCase,
                                browserConfigs: newConfigs
                              });
                            }
                          }
                        }}
                        isOpen={userAgentDropdowns[config.id] || false}
                        setIsOpen={(open) => setUserAgentDropdowns(prev => ({ ...prev, [config.id]: open }))}
                        placeholder="Select User Agent"
                        fullWidth={true}
                      />
                      {(commonUserAgents.find(ua => ua.value === config.userAgent)?.value === 'custom' || 
                        !commonUserAgents.find(ua => ua.value === config.userAgent)) && (
                        <textarea
                          value={config.userAgent}
                          onChange={(e) => {
                            if (editableTestCase) {
                              const newConfigs = [...editableTestCase.browserConfigs];
                              newConfigs[index] = { ...newConfigs[index], userAgent: e.target.value };
                              setEditableTestCase({
                                ...editableTestCase,
                                browserConfigs: newConfigs
                              });
                            }
                          }}
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none text-xs"
                          rows={2}
                          placeholder="Enter custom user agent string"
                        />
                      )}
                    </div>
                  </div>
                  
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Viewport resolution</label>
                    <div className="space-y-2">
                      <CustomDropdown
                        options={commonViewports}
                        value={(() => {
                          const currentResolution = `${config.viewport.width}x${config.viewport.height}`;
                          return commonViewports.find(vp => vp.value === currentResolution)?.value || 'custom';
                        })()}
                        onChange={(value) => {
                          if (editableTestCase && value !== 'custom') {
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
                        placeholder="Select Viewport Resolution"
                        fullWidth={true}
                      />
                      {(() => {
                        const currentResolution = `${config.viewport.width}x${config.viewport.height}`;
                        return !commonViewports.find(vp => vp.value === currentResolution) || 
                               commonViewports.find(vp => vp.value === currentResolution)?.value === 'custom';
                      })() && (
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-500 mb-1">Width</label>
                            <input
                              type="number"
                              value={config.viewport.width}
                              onChange={(e) => {
                                if (editableTestCase) {
                                  const newConfigs = [...editableTestCase.browserConfigs];
                                  newConfigs[index] = {
                                    ...newConfigs[index],
                                    viewport: { ...newConfigs[index].viewport, width: parseInt(e.target.value) || 0 }
                                  };
                                  setEditableTestCase({
                                    ...editableTestCase,
                                    browserConfigs: newConfigs
                                  });
                                }
                              }}
                              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                              placeholder="Width"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-500 mb-1">Height</label>
                            <input
                              type="number"
                              value={config.viewport.height}
                              onChange={(e) => {
                                if (editableTestCase) {
                                  const newConfigs = [...editableTestCase.browserConfigs];
                                  newConfigs[index] = {
                                    ...newConfigs[index],
                                    viewport: { ...newConfigs[index].viewport, height: parseInt(e.target.value) || 0 }
                                  };
                                  setEditableTestCase({
                                    ...editableTestCase,
                                    browserConfigs: newConfigs
                                  });
                                }
                              }}
                              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                              placeholder="Height"
                            />
                          </div>
                        </div>
                      )}
                    </div>
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
                      className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
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
                      className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
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
                <Monitor className="w-5 h-5 text-gray-600" />
                <h3 className="font-medium text-gray-800">{config.name}</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">User agent</label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded text-gray-700 text-xs break-all">
                    {config.userAgent}
                  </div>
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Viewport</label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded text-gray-700">
                    {config.viewport.width} × {config.viewport.height}
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
            <Shield className="w-5 h-5 text-gray-600" />
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
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Secret
                  </button>
                  <button
                    onClick={handleSaveSecrets}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Save className="w-4 h-4 mr-1" />
                    Save
                  </button>
                  <button
                    onClick={handleCancelSecrets}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
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
            to={`/history?testCase=${testCase.id}`}
            className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
          >
            <History className="w-4 h-4 mr-1" />
            View All Runs
          </Link>
        </div>
        
        <div className="space-y-3">
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
                <div key={run.id} className="flex items-start space-x-4 p-4 bg-gray-50 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
                  {/* GIF Display */}
                  {runGif && (
                    <div className="flex-shrink-0">
                      <img 
                        src={runGif} 
                        alt="Test run animation"
                        className="w-24 h-16 object-cover rounded-lg border border-gray-300"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          {status === 'FINISHED' ? (
                            <CheckCircle className="w-5 h-5 text-emerald-500" />
                          ) : status === 'FAILED' ? (
                            <X className="w-5 h-5 text-red-500" />
                          ) : (
                            <Clock className="w-5 h-5 text-yellow-500" />
                          )}
                          <span className={`text-sm font-medium capitalize ${
                            status === 'FINISHED' ? 'text-emerald-600' :
                            status === 'FAILED' ? 'text-red-600' :
                            'text-yellow-600'
                          }`}>
                            {status.toLowerCase()}
                          </span>
                        </div>
                        
                        {totalSteps > 0 && (
                          <div className="text-sm text-gray-600">
                            {passedSteps}/{totalSteps} steps passed
                          </div>
                        )}
                        
                        <div className="flex items-center space-x-1 text-sm text-gray-500">
                          <Calendar className="w-4 h-4" />
                          <span>{startedAt.toLocaleDateString()}</span>
                        </div>
                        
                        {duration > 0 && (
                          <div className="flex items-center space-x-1 text-sm text-gray-500">
                            <Clock className="w-4 h-4" />
                            <span>{duration.toFixed(1)}s</span>
                          </div>
                        )}
                        
                        {runType && (
                          <div className="text-sm text-gray-500">
                            <span className="font-medium">Type:</span> {runType}
                          </div>
                        )}
                        
                        {origin && (
                          <div className="text-sm text-gray-500">
                            <span className="font-medium">Origin:</span> {origin}
                          </div>
                        )}
                        
                        {browserConfig?.browser_config?.viewport && (
                          <div className="flex items-center space-x-1 text-sm text-gray-500">
                            <Monitor className="w-4 h-4" />
                            <span>{browserConfig.browser_config.viewport.width}×{browserConfig.browser_config.viewport.height}</span>
                          </div>
                        )}
                      </div>
                      
                      <Link
                        to={`/history/${run.id}`}
                        className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        View Details
                      </Link>
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
                to={`/history/${testCase.id}/run`}
                className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <Play className="w-4 h-4 mr-2" />
                Run Test Now
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