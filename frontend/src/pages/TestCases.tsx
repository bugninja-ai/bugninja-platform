import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  SkipForward, 
  Filter, 
  Search,
  TrendingUp,
  Target,
  Play,
  Calendar,
  MoreHorizontal
} from 'lucide-react';
import { TestCase, TestStatistics, TestFilters } from '../types';
import { mockApi } from '../data/mockData';

const STATUS_COLORS = {
  passed: 'text-green-600 bg-green-50 border-green-200',
  failed: 'text-red-600 bg-red-50 border-red-200',
  pending: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  skipped: 'text-gray-600 bg-gray-50 border-gray-200',
} as const;

const PRIORITY_COLORS = {
  critical: 'text-red-600 bg-red-50',
  high: 'text-orange-600 bg-orange-50',
  medium: 'text-blue-600 bg-blue-50',
  low: 'text-gray-600 bg-gray-50',
} as const;

export const TestCases: React.FC = () => {
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [statistics, setStatistics] = useState<TestStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<TestFilters>({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [casesData, statsData] = await Promise.all([
        mockApi.getTestCases(),
        mockApi.getStatistics()
      ]);
      setTestCases(casesData);
      setStatistics(statsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const runTest = async (testCaseId: string) => {
    try {
      await mockApi.runTest(testCaseId);
      await loadData();
    } catch (error) {
      console.error('Failed to run test:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading test cases...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Banking Software Test Cases</h1>
          <p className="text-gray-600 dark:text-gray-400">Automated E2E test cases for core banking functionality</p>
        </div>

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-8">
            <div className="bg-white dark:bg-gray-800 border border-green-200 dark:border-green-700 rounded-lg p-4 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-green-700 dark:text-green-400">Passed</span>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-green-600">{statistics.passedTests}</div>
            </div>

            <div className="bg-white dark:bg-gray-800 border border-red-200 dark:border-red-700 rounded-lg p-4 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-red-700 dark:text-red-400">Failed</span>
                <XCircle className="h-4 w-4 text-red-600" />
              </div>
              <div className="text-2xl font-bold text-red-600">{statistics.failedTests}</div>
            </div>

            <div className="bg-white dark:bg-gray-800 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-yellow-700 dark:text-yellow-400">Pending</span>
                <Clock className="h-4 w-4 text-yellow-600" />
              </div>
              <div className="text-2xl font-bold text-yellow-600">{statistics.pendingTests}</div>
            </div>

            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-400">Skipped</span>
                <SkipForward className="h-4 w-4 text-gray-600" />
              </div>
              <div className="text-2xl font-bold text-gray-600">{statistics.skippedTests}</div>
            </div>

            <div className="bg-white dark:bg-gray-800 border border-blue-200 dark:border-blue-700 rounded-lg p-4 shadow-sm col-span-2">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-700 dark:text-blue-400">Pass Rate</span>
                <TrendingUp className="h-4 w-4 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-blue-600">{statistics.passRate}%</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-900 dark:text-white">Filter Test Cases</span>
            </div>
            <span className="text-sm text-gray-600 dark:text-gray-400">{testCases.length} of {testCases.length} tests</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search test cases..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={filters.search || ''}
                onChange={(e) => setFilters({...filters, search: e.target.value})}
              />
            </div>

            {/* Status Filter */}
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="">All Statuses</option>
              <option value="passed">Passed</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
              <option value="skipped">Skipped</option>
            </select>

            {/* Priority Filter */}
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="">All Priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>

            {/* Category Filter */}
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="">All Categories</option>
              <option value="authentication">Authentication</option>
              <option value="banking">Banking</option>
              <option value="payments">Payments</option>
              <option value="security">Security</option>
            </select>
          </div>
        </div>

        {/* Test Cases List */}
        <div className="space-y-4">
          {testCases.map((testCase) => (
            <div key={testCase.id} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <Link 
                      to={`/test-cases/${testCase.id}`}
                      className="text-lg font-semibold text-gray-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                    >
                      {testCase.title}
                    </Link>
                    <span className="text-sm text-gray-600 dark:text-gray-400 font-mono">{testCase.code}</span>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400 mb-3">{testCase.description}</p>
                  
                  <div className="flex items-center space-x-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${STATUS_COLORS[testCase.status]}`}>
                      {testCase.status === 'passed' && <CheckCircle className="h-3 w-3 mr-1" />}
                      {testCase.status === 'failed' && <XCircle className="h-3 w-3 mr-1" />}
                      {testCase.status === 'pending' && <Clock className="h-3 w-3 mr-1" />}
                      {testCase.status === 'skipped' && <SkipForward className="h-3 w-3 mr-1" />}
                      {testCase.status.charAt(0).toUpperCase() + testCase.status.slice(1)}
                    </span>
                    
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${PRIORITY_COLORS[testCase.priority]}`}>
                      {testCase.priority.charAt(0).toUpperCase() + testCase.priority.slice(1)}
                    </span>
                    
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200">
                      {testCase.category}
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => runTest(testCase.id)}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-indigo-600 bg-indigo-100 hover:bg-indigo-200 dark:text-indigo-400 dark:bg-indigo-900 dark:hover:bg-indigo-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Run Test
                  </button>
                  
                  <button className="p-1.5 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Test Goal */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-3 mb-4">
                <div className="flex items-center space-x-2 mb-1">
                  <Target className="h-4 w-4 text-indigo-600" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">Test Goal</span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{testCase.goal}</p>
              </div>

              {/* Test Metrics */}
              <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                <div className="flex items-center space-x-4">
                  <span className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>Last run: {testCase.lastRunAt ? new Date(testCase.lastRunAt).toLocaleDateString() : 'Never'}</span>
                  </span>
                  <span>Duration: 2.3s</span>
                </div>
                
                <div className="flex items-center space-x-1">
                  <span className="font-medium">Passed Steps</span>
                  <span className="text-green-600">6/8</span>
                  <span className="ml-2 font-medium">Failed Steps</span>
                  <span className="text-red-600">2/8</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}; 