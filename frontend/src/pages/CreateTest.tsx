import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  Plus, 
  X,
  AlertCircle,
  CheckCircle,
  Loader2,
  Trash2,
  Globe,
  Monitor
} from 'lucide-react';
import { CustomDropdown } from '../components/CustomDropdown';

const CreateTest: React.FC = () => {
  const navigate = useNavigate();
  const [method, setMethod] = useState<'upload' | 'manual'>('manual');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  
  // Dropdown states
  const [priorityDropdownOpen, setPriorityDropdownOpen] = useState(false);
  const [categoryDropdownOpen, setCategoryDropdownOpen] = useState(false);
  const [userAgentDropdowns, setUserAgentDropdowns] = useState<Record<string, boolean>>({});
  const [viewportDropdowns, setViewportDropdowns] = useState<Record<string, boolean>>({});

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
  
  // Form data
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    category: 'authentication',
    goal: '',
    startingUrl: '',
    allowedDomains: [''],
    extraRules: [{ id: '1', ruleNumber: 1, description: '' }],
    browserConfigs: [{
      id: '1',
      name: 'Desktop Chrome',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      viewport: { width: 1920, height: 1080 },
      geolocation: undefined as { latitude: number; longitude: number; } | undefined
    }],
    secrets: [] as { id: string; secretName: string; value: string; }[]
  });

  const [file, setFile] = useState<File | null>(null);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Extra Rules handlers
  const handleRuleChange = (index: number, value: string) => {
    const newRules = [...formData.extraRules];
    newRules[index] = { ...newRules[index], description: value };
    setFormData(prev => ({
      ...prev,
      extraRules: newRules
    }));
  };

  const addRule = () => {
    const newRule = {
      id: `rule-${Date.now()}`,
      ruleNumber: formData.extraRules.length + 1,
      description: ''
    };
    setFormData(prev => ({
      ...prev,
      extraRules: [...prev.extraRules, newRule]
    }));
  };

  const removeRule = (index: number) => {
    if (formData.extraRules.length > 1) {
      const newRules = formData.extraRules.filter((_, i) => i !== index);
      // Renumber remaining rules
      const renumberedRules = newRules.map((rule, i) => ({ ...rule, ruleNumber: i + 1 }));
      setFormData(prev => ({
        ...prev,
        extraRules: renumberedRules
      }));
    }
  };

  // Allowed Domains handlers
  const handleDomainChange = (index: number, value: string) => {
    const newDomains = [...formData.allowedDomains];
    newDomains[index] = value;
    setFormData(prev => ({
      ...prev,
      allowedDomains: newDomains
    }));
  };

  const addDomain = () => {
    setFormData(prev => ({
      ...prev,
      allowedDomains: [...prev.allowedDomains, '']
    }));
  };

  const removeDomain = (index: number) => {
    if (formData.allowedDomains.length > 1) {
      const newDomains = formData.allowedDomains.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        allowedDomains: newDomains
      }));
    }
  };

  // Browser Config handlers
  const handleBrowserConfigChange = (index: number, field: string, value: any) => {
    const newConfigs = [...formData.browserConfigs];
    if (field === 'viewport.width' || field === 'viewport.height') {
      const [, dimension] = field.split('.');
      newConfigs[index] = {
        ...newConfigs[index],
        viewport: { ...newConfigs[index].viewport, [dimension]: value }
      };
    } else if (field.startsWith('geolocation.')) {
      const [, coord] = field.split('.');
      const currentGeo = newConfigs[index].geolocation || { latitude: 0, longitude: 0 };
      newConfigs[index] = {
        ...newConfigs[index],
        geolocation: { ...currentGeo, [coord]: value }
      };
    } else {
      newConfigs[index] = { ...newConfigs[index], [field]: value };
    }
    setFormData(prev => ({
      ...prev,
      browserConfigs: newConfigs
    }));
  };

  const addBrowserConfig = () => {
    const newConfig = {
      id: `config-${Date.now()}`,
      name: 'New Configuration',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      viewport: { width: 1920, height: 1080 },
      geolocation: undefined
    };
    setFormData(prev => ({
      ...prev,
      browserConfigs: [...prev.browserConfigs, newConfig]
    }));
  };

  const removeBrowserConfig = (index: number) => {
    if (formData.browserConfigs.length > 1) {
      const newConfigs = formData.browserConfigs.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        browserConfigs: newConfigs
      }));
    }
  };

  // Secrets handlers
  const handleSecretChange = (index: number, field: string, value: string) => {
    const newSecrets = [...formData.secrets];
    newSecrets[index] = { ...newSecrets[index], [field]: value };
    setFormData(prev => ({
      ...prev,
      secrets: newSecrets
    }));
  };

  const addSecret = () => {
    const newSecret = {
      id: `secret-${Date.now()}`,
      secretName: '',
      value: ''
    };
    setFormData(prev => ({
      ...prev,
      secrets: [...prev.secrets, newSecret]
    }));
  };

  const removeSecret = (index: number) => {
    const newSecrets = formData.secrets.filter((_, i) => i !== index);
    setFormData(prev => ({
      ...prev,
      secrets: newSecrets
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      setSuccess(true);
      
      setTimeout(() => {
        navigate('/');
      }, 1500);
    } catch (error) {
      console.error('Failed to create test case:', error);
    } finally {
      setLoading(false);
    }
  };

  const priorityOptions = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' },
  ];

  const categoryOptions = [
    { value: 'authentication', label: 'Authentication' },
    { value: 'banking', label: 'Banking' },
    { value: 'payments', label: 'Payments' },
    { value: 'security', label: 'Security' },
    { value: 'ui', label: 'UI' },
    { value: 'api', label: 'API' },
  ];



  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-8 border border-gray-200 text-center max-w-md mx-auto">
          <div className="w-16 h-16 bg-emerald-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-emerald-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Test Case Created!</h3>
          <p className="text-gray-600">Your test case has been successfully created and is ready to run.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Create Test Case</h1>
        <p className="mt-1 text-gray-600">Create a new automated test case for your application</p>
      </div>

      {/* Method Selection */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Choose Creation Method</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => setMethod('manual')}
            className={`p-6 rounded-lg border-2 transition-colors ${
              method === 'manual'
                ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                : 'border-gray-200 bg-white hover:border-gray-300 text-gray-700'
            }`}
          >
            <FileText className="w-8 h-8 mx-auto mb-3" />
            <h3 className="font-semibold mb-2">Manual Entry</h3>
            <p className="text-sm">Create test case by filling out the form manually</p>
          </button>
          
          <button
            onClick={() => setMethod('upload')}
            className={`p-6 rounded-lg border-2 transition-colors ${
              method === 'upload'
                ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                : 'border-gray-200 bg-white hover:border-gray-300 text-gray-700'
            }`}
          >
            <Upload className="w-8 h-8 mx-auto mb-3" />
            <h3 className="font-semibold mb-2">File Upload</h3>
            <p className="text-sm">Upload a test case file (.csv, .json, .txt, .doc, .docx, .pdf, .xlsx)</p>
          </button>
        </div>
      </div>

      {/* Form Content */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {method === 'upload' ? (
          <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Upload Test Case File</h2>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-indigo-400 transition-colors">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Upload your test case file</h3>
              <p className="text-gray-600 mb-4">Drag and drop your file here, or click to select</p>
              
              <input
                type="file"
                accept=".csv,.json,.txt,.doc,.docx,.pdf,.xlsx,.xls,.rtf,.odt"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors cursor-pointer"
              >
                Select File
              </label>
              
              {file && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg flex items-center justify-between">
                  <span className="text-sm text-gray-700">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => setFile(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Basic Information */}
            <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Basic Information</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test Case Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
                    placeholder="e.g., User Login Authentication"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Priority *
                  </label>
                  <CustomDropdown
                    options={priorityOptions}
                    value={formData.priority}
                    onChange={(value) => handleInputChange('priority', value)}
                    isOpen={priorityDropdownOpen}
                    setIsOpen={setPriorityDropdownOpen}
                    placeholder="Select Priority"
                    fullWidth={true}
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category *
                  </label>
                  <CustomDropdown
                    options={categoryOptions}
                    value={formData.category}
                    onChange={(value) => handleInputChange('category', value)}
                    isOpen={categoryDropdownOpen}
                    setIsOpen={setCategoryDropdownOpen}
                    placeholder="Select Category"
                    fullWidth={true}
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                  </label>
                  <textarea
                    required
                    rows={3}
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
                    placeholder="Describe what this test case validates..."
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test Goal *
                  </label>
                  <textarea
                    required
                    rows={2}
                    value={formData.goal}
                    onChange={(e) => handleInputChange('goal', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
                    placeholder="What should this test achieve or verify?"
                  />
                </div>
              </div>
            </div>

            {/* Test Configuration */}
            <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Test Configuration</h2>
              
              <div className="space-y-6">
                {/* Starting URL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Starting URL *</label>
                  <div className="flex items-center space-x-2">
                    <Globe className="w-4 h-4 text-gray-400 ml-3" />
                    <input
                      type="url"
                      required
                      value={formData.startingUrl}
                      onChange={(e) => handleInputChange('startingUrl', e.target.value)}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
                      placeholder="https://example.com"
                    />
                  </div>
                </div>

                {/* Allowed Domains */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">Allowed Domains *</label>
                    <button
                      type="button"
                      onClick={addDomain}
                      className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      Add Domain
                    </button>
                  </div>
                  <div className="space-y-2">
                    {formData.allowedDomains.map((domain, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <Globe className="w-4 h-4 text-gray-400 ml-3" />
                        <input
                          type="text"
                          value={domain}
                          onChange={(e) => handleDomainChange(index, e.target.value)}
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
                          placeholder="example.com"
                        />
                        {formData.allowedDomains.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeDomain(index)}
                            className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Browser Configurations */}
            <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-800">Browser Configurations</h2>
                <button
                  type="button"
                  onClick={addBrowserConfig}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Config
                </button>
              </div>

              <div className="space-y-4">
                {formData.browserConfigs.map((config, index) => (
                  <div key={config.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <Monitor className="w-5 h-5 text-gray-600" />
                        <input
                          type="text"
                          value={config.name}
                          onChange={(e) => handleBrowserConfigChange(index, 'name', e.target.value)}
                          className="font-medium text-gray-800 bg-transparent border-b border-gray-300 focus:border-indigo-500 focus:outline-none"
                          placeholder="Configuration name"
                        />
                      </div>
                      {formData.browserConfigs.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeBrowserConfig(index)}
                          className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div className="md:col-span-2">
                        <label className="block text-xs font-medium text-gray-500 mb-1">User Agent</label>
                        <div className="space-y-2">
                          <CustomDropdown
                            options={commonUserAgents}
                            value={commonUserAgents.find(ua => ua.value === config.userAgent)?.value || 'custom'}
                            onChange={(value) => {
                              if (value !== 'custom') {
                                handleBrowserConfigChange(index, 'userAgent', value);
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
                              onChange={(e) => handleBrowserConfigChange(index, 'userAgent', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none text-xs bg-white"
                              rows={2}
                              placeholder="Enter custom user agent string"
                            />
                          )}
                        </div>
                      </div>
                      
                      <div className="md:col-span-2">
                        <label className="block text-xs font-medium text-gray-500 mb-1">Viewport Resolution</label>
                        <div className="space-y-2">
                          <CustomDropdown
                            options={commonViewports}
                            value={(() => {
                              const currentResolution = `${config.viewport.width}x${config.viewport.height}`;
                              return commonViewports.find(vp => vp.value === currentResolution)?.value || 'custom';
                            })()}
                            onChange={(value) => {
                              if (value !== 'custom') {
                                const [width, height] = value.split('x').map(Number);
                                handleBrowserConfigChange(index, 'viewport.width', width);
                                handleBrowserConfigChange(index, 'viewport.height', height);
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
                                  onChange={(e) => handleBrowserConfigChange(index, 'viewport.width', parseInt(e.target.value) || 0)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
                                  placeholder="Width"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-500 mb-1">Height</label>
                                <input
                                  type="number"
                                  value={config.viewport.height}
                                  onChange={(e) => handleBrowserConfigChange(index, 'viewport.height', parseInt(e.target.value) || 0)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
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
                            const value = e.target.value;
                            if (value) {
                              handleBrowserConfigChange(index, 'geolocation.latitude', parseFloat(value));
                            } else {
                              handleBrowserConfigChange(index, 'geolocation', undefined);
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
                            const value = e.target.value;
                            if (value) {
                              handleBrowserConfigChange(index, 'geolocation.longitude', parseFloat(value));
                            } else if (!config.geolocation?.latitude) {
                              handleBrowserConfigChange(index, 'geolocation', undefined);
                            }
                          }}
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
                          placeholder="e.g. -74.0060"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Secrets */}
            {formData.secrets.length > 0 && (
              <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-800">Secrets</h2>
                  <button
                    type="button"
                    onClick={addSecret}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Secret
                  </button>
                </div>
                
                <div className="space-y-3">
                  {formData.secrets.map((secret, index) => (
                    <div key={secret.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <input
                          type="text"
                          value={secret.secretName}
                          onChange={(e) => handleSecretChange(index, 'secretName', e.target.value)}
                          className="text-sm font-medium text-gray-700 bg-transparent border-b border-gray-300 focus:border-indigo-500 focus:outline-none flex-1 mr-4"
                          placeholder="Secret name"
                        />
                        <button
                          type="button"
                          onClick={() => removeSecret(index)}
                          className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      
                      <div>
                        <input
                          type="password"
                          value={secret.value}
                          onChange={(e) => handleSecretChange(index, 'value', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-gray-800 font-mono text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
                          placeholder="Secret value"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Add Secrets Button - Show when no secrets exist */}
            {formData.secrets.length === 0 && (
              <div className="text-center">
                <button
                  type="button"
                  onClick={addSecret}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Secrets (Optional)
                </button>
              </div>
            )}

            {/* Extra Rules */}
            <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-800">Extra Rules</h2>
                <button
                  type="button"
                  onClick={addRule}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Rule
                </button>
              </div>

              <div className="space-y-3">
                {formData.extraRules.map((rule, index) => (
                  <div key={rule.id} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-sm font-medium text-indigo-600 mt-1">
                      {rule.ruleNumber}
                    </div>
                    <div className="flex-1">
                      <textarea
                        value={rule.description}
                        onChange={(e) => handleRuleChange(index, e.target.value)}
                        placeholder={`Rule ${rule.ruleNumber}: Describe the rule or constraint...`}
                        rows={2}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
                      />
                    </div>
                    {formData.extraRules.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeRule(index)}
                        className="flex-shrink-0 p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors mt-1"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-6">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-6 py-3 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
          
          <button
            type="submit"
            disabled={loading || (method === 'upload' && !file) || (method === 'manual' && (!formData.title || !formData.description || !formData.goal || !formData.startingUrl || formData.allowedDomains.some(domain => !domain.trim())))}
            className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="w-4 h-4 mr-2" />
                Create Test Case
              </>
            )}
          </button>
        </div>
      </form>

      {/* Help Information */}
      <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-blue-900 mb-1">Need Help?</h3>
            <p className="text-sm text-blue-800">
              Test cases should be clear, specific, and include all necessary steps to validate the expected behavior. 
              For file uploads, we support CSV, JSON, TXT, DOC, DOCX, PDF, XLSX, XLS, RTF, and ODT formats with predefined structures.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateTest; 