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
  AlertCircle
} from 'lucide-react';
import { TestCase } from '../types';
import { mockApi } from '../data/mockData';

const TestCaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [testCase, setTestCase] = useState<TestCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [visibleSecrets, setVisibleSecrets] = useState<Set<string>>(new Set());
  const [copiedSecret, setCopiedSecret] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadTestCase(id);
    }
  }, [id]);

  const loadTestCase = async (testCaseId: string) => {
    try {
      setLoading(true);
      const tc = await mockApi.getTestCase(testCaseId);
      setTestCase(tc);
    } catch (error) {
      console.error('Failed to load test case:', error);
    } finally {
      setLoading(false);
    }
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
    switch (status) {
      case 'passed':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-blue-500" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading test case details...</p>
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
                testCase.status === 'pending' ? 'text-blue-600' :
                'text-yellow-600'
              }`}>
                {testCase.status.charAt(0).toUpperCase() + testCase.status.slice(1)}
              </span>
            </div>
          </div>
          <p className="text-gray-600 mb-4">{testCase.description}</p>
          
          {/* Test Goal */}
          <div className="bg-blue-50 rounded-lg p-4 mb-4 max-w-2xl">
            <div className="flex items-center space-x-2 mb-2">
              <Target className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-semibold text-blue-900">Test Goal</span>
            </div>
            <p className="text-sm text-blue-800">{testCase.goal}</p>
          </div>
        </div>

        <Link
          to="/"
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Test Cases
        </Link>
      </div>

      {/* Basic Information */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Basic Information</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Test Case ID</label>
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
            <div className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800 capitalize">
              {testCase.category}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Created</label>
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span>{testCase.createdAt.toLocaleDateString()}</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Last Updated</label>
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span>{testCase.updatedAt.toLocaleDateString()}</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Total Runs</label>
            <div className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
              {testCase.totalRuns}
            </div>
          </div>
        </div>
      </div>

      {/* Test Configuration */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Test Configuration</h2>
        
        <div className="space-y-6">
          {/* Starting URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Starting URL</label>
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
              <Globe className="w-4 h-4 text-gray-400" />
              <span className="break-all">{testCase.startingUrl}</span>
            </div>
          </div>

          {/* Allowed Domains */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Allowed Domains</label>
            <div className="space-y-2">
              {testCase.allowedDomains.map((domain, index) => (
                <div key={index} className="flex items-center space-x-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800">
                  <Globe className="w-4 h-4 text-gray-400" />
                  <span>{domain}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Extra Rules */}
      {testCase.extraRules.length > 0 && (
        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Extra Rules</h2>
          
          <div className="space-y-3">
            {testCase.extraRules.map((rule) => (
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
            ))}
          </div>
        </div>
      )}

      {/* Browser Configurations */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Browser Configurations</h2>
        
        <div className="space-y-4">
          {testCase.browserConfigs.map((config) => (
            <div key={config.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Monitor className="w-5 h-5 text-gray-600" />
                <h3 className="font-medium text-gray-800">{config.name}</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">User Agent</label>
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
                
                {config.geolocation && (
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
          ))}
        </div>
      </div>

      {/* Secrets */}
      {testCase.secrets.length > 0 && (
        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <Shield className="w-5 h-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-800">Secrets</h2>
          </div>
          
          <div className="space-y-3">
            {testCase.secrets.map((secret) => (
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
            ))}
          </div>
        </div>
      )}

      {/* Run History Summary */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Execution Summary</h2>
        
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