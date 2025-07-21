import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Calendar, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Filter,
  Search,
  Play,
  Eye,
  Monitor
} from 'lucide-react';
import { TestRun } from '../types';
import { mockTestRuns } from '../data/mockData';
import { CustomDropdown } from '../components/CustomDropdown';

const TestHistory: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');
  
  // Dropdown states
  const [statusDropdownOpen, setStatusDropdownOpen] = useState(false);
  const [dateDropdownOpen, setDateDropdownOpen] = useState(false);

  const testRuns = mockTestRuns;

  const filteredRuns = testRuns.filter((run: TestRun) => {
    const matchesSearch = run.testCase.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         run.testCase.code.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || run.status === statusFilter;
    
    let matchesDate = true;
    if (dateFilter !== 'all') {
      const runDate = new Date(run.startedAt);
      const now = new Date();
      const daysAgo = Math.floor((now.getTime() - runDate.getTime()) / (1000 * 60 * 60 * 24));
      
      switch (dateFilter) {
        case 'today':
          matchesDate = daysAgo === 0;
          break;
        case 'week':
          matchesDate = daysAgo <= 7;
          break;
        case 'month':
          matchesDate = daysAgo <= 30;
          break;
      }
    }
    
    return matchesSearch && matchesStatus && matchesDate;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'text-emerald-600 bg-emerald-50 border-emerald-200';
      case 'failed':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) {
      return `${Math.round(seconds)}s`;
    } else {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = Math.round(seconds % 60);
      return `${minutes}m ${remainingSeconds}s`;
    }
  };

  const getBrowserInfo = (run: TestRun) => {
    // Try to find the matching browser config from the test case
    const browserConfig = run.testCase.browserConfigs.find(config => 
      config.userAgent === run.userAgent || 
      config.name.toLowerCase().includes(run.browser.toLowerCase().split(' ')[0])
    );
    
    if (browserConfig) {
      return {
        name: browserConfig.name,
        resolution: `${browserConfig.viewport.width}x${browserConfig.viewport.height}`
      };
    }
    
    // Fallback if no config found
    return {
      name: run.browser,
      resolution: 'Unknown resolution'
    };
  };

  const statusOptions = [
    { value: 'all', label: 'All statuses' },
    { value: 'passed', label: 'Passed' },
    { value: 'failed', label: 'Failed' },
    { value: 'pending', label: 'Pending' },
  ];

  const dateOptions = [
    { value: 'all', label: 'All time' },
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'Last week' },
    { value: 'month', label: 'Last month' },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Test runs</h1>
          <p className="mt-1 text-gray-600">View and analyze past test run results</p>
        </div>
        <div className="mt-4 sm:mt-0 text-sm text-gray-500">
          {filteredRuns.length} of {testRuns.length} test runs
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total runs</p>
              <p className="text-3xl font-bold text-gray-800">{testRuns.length}</p>
            </div>
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
              <Play className="w-6 h-6 text-indigo-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-indigo-600 font-medium">Last 30 days</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success rate</p>
              <p className="text-3xl font-bold text-emerald-600">
                {Math.round((testRuns.filter(r => r.status === 'passed').length / testRuns.length) * 100)}%
              </p>
            </div>
            <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-emerald-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-emerald-600 font-medium">+5%</span>
            <span className="text-gray-600 ml-1">from last week</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg duration</p>
              <p className="text-3xl font-bold text-blue-600">
                {formatDuration(testRuns.reduce((acc, run) => acc + run.duration, 0) / testRuns.length)}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-blue-600 font-medium">Improving</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <span className="font-medium text-gray-800">Filter test runs</span>
          </div>
          
          <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search test runs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 w-full sm:w-64 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
              />
            </div>

            {/* Status Filter */}
            <CustomDropdown
              options={statusOptions}
              value={statusFilter}
              onChange={setStatusFilter}
              isOpen={statusDropdownOpen}
              setIsOpen={setStatusDropdownOpen}
              placeholder="All statuses"
            />

            {/* Date Filter */}
            <CustomDropdown
              options={dateOptions}
              value={dateFilter}
              onChange={setDateFilter}
              isOpen={dateDropdownOpen}
              setIsOpen={setDateDropdownOpen}
              placeholder="All time"
            />
          </div>
        </div>
      </div>

      {/* Test Runs List */}
      <div className="space-y-3">
        {filteredRuns.map((run: TestRun) => {
          const browserInfo = getBrowserInfo(run);
          
          return (
            <div key={run.id} className="bg-white rounded-lg p-6 border border-gray-200 hover:border-gray-300 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-800">{run.testCase.title}</h3>
                    <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-lg">{run.testCase.code}</span>
                    <span className={`inline-flex items-center text-xs font-medium px-2 py-1 rounded-lg border ${getStatusColor(run.status)}`}>
                      {getStatusIcon(run.status)}
                      <span className="ml-1">{run.status.charAt(0).toUpperCase() + run.status.slice(1)}</span>
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-3">{run.testCase.description}</p>

                  {/* Browser and Resolution Info */}
                  <div className="flex items-center space-x-4 mb-4 text-sm text-gray-600">
                    <div className="flex items-center space-x-1">
                      <Monitor className="w-4 h-4 text-gray-400" />
                      <span>{browserInfo.name}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-400">•</span>
                      <span>{browserInfo.resolution}</span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <Calendar className="w-4 h-4" />
                      <span>Started: {new Date(run.startedAt).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>Duration: {formatDuration(run.duration)}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-400">Steps:</span>
                      <span className="text-emerald-600 font-medium">{run.passedSteps}</span>
                      <span className="text-gray-400">/</span>
                      <span className="text-red-600 font-medium">{run.failedSteps}</span>
                      <span className="text-gray-400">/</span>
                      <span className="font-medium">{run.totalSteps}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-400">Environment:</span>
                      <span className="text-gray-600 font-medium">{run.environment}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 ml-4">
                  <Link
                    to={`/history/${run.id}`}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    View details
                  </Link>
                </div>
              </div>
            </div>
          );
        })}

        {filteredRuns.length === 0 && (
          <div className="bg-white rounded-lg p-12 border border-gray-200 text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Clock className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">No test runs found</h3>
            <p className="text-gray-600 mb-6">Try adjusting your filters or run some tests to see results here.</p>
            <Link
              to="/"
              className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
            >
              View test cases
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default TestHistory; 