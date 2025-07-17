import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { createPortal } from 'react-dom';
import { 
  Plus, 
  Filter, 
  Search, 
  Play, 
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  ChevronDown
} from 'lucide-react';
import { TestCase } from '../types';
import { mockTestCases, mockStatistics } from '../data/mockData';

const TestCases: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  
  // Dropdown states
  const [statusDropdownOpen, setStatusDropdownOpen] = useState(false);
  const [priorityDropdownOpen, setPriorityDropdownOpen] = useState(false);
  const [categoryDropdownOpen, setCategoryDropdownOpen] = useState(false);

  const testCases = mockTestCases;
  const stats = mockStatistics;

  const filteredTestCases = testCases.filter((testCase: TestCase) => {
    const matchesSearch = testCase.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         testCase.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || testCase.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || testCase.priority === priorityFilter;
    const matchesCategory = categoryFilter === 'all' || testCase.category === categoryFilter;
    
    return matchesSearch && matchesStatus && matchesPriority && matchesCategory;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-blue-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
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

  const statusOptions = [
    { value: 'all', label: 'All Statuses' },
    { value: 'passed', label: 'Passed' },
    { value: 'failed', label: 'Failed' },
    { value: 'pending', label: 'Pending' },
    { value: 'skipped', label: 'Skipped' },
  ];

  const priorityOptions = [
    { value: 'all', label: 'All Priorities' },
    { value: 'critical', label: 'Critical' },
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' },
  ];

  const categoryOptions = [
    { value: 'all', label: 'All Categories' },
    { value: 'authentication', label: 'Authentication' },
    { value: 'banking', label: 'Banking' },
    { value: 'payments', label: 'Payments' },
    { value: 'security', label: 'Security' },
    { value: 'ui', label: 'UI' },
    { value: 'api', label: 'API' },
  ];

  const CustomDropdown = ({ 
    options, 
    value, 
    onChange, 
    isOpen, 
    setIsOpen, 
    placeholder 
  }: {
    options: { value: string; label: string }[];
    value: string;
    onChange: (value: string) => void;
    isOpen: boolean;
    setIsOpen: (open: boolean) => void;
    placeholder: string;
  }) => {
    const selectedOption = options.find(option => option.value === value);
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
          onClick={() => setIsOpen(!isOpen)}
          className="w-40 bg-white border border-gray-300 rounded-lg px-4 py-2 text-left flex items-center justify-between hover:border-gray-400 transition-colors focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <span className="text-gray-800">{selectedOption?.label || placeholder}</span>
          <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>
        
        {isOpen && createPortal(
          <>
            <div 
              className="fixed inset-0 z-[9998]" 
              onClick={() => setIsOpen(false)}
            />
                         <div 
               className="fixed bg-white border border-gray-300 rounded-lg overflow-hidden shadow-xl z-[9999] w-40"
               style={{
                 top: `${getDropdownPosition().top}px`,
                 left: `${getDropdownPosition().left}px`,
                 maxHeight: '240px',
                 overflowY: 'auto'
               }}
             >
              {options.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => {
                    onChange(option.value);
                    setIsOpen(false);
                  }}
                  className={`w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors text-gray-800 ${
                    option.value === value ? 'bg-indigo-50 text-indigo-700' : ''
                  }`}
                >
                  {option.label}
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Test Cases</h1>
          <p className="mt-1 text-gray-600">Manage and monitor your automated test cases</p>
        </div>
        <Link
          to="/create"
          className="mt-4 sm:mt-0 inline-flex items-center px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          Create Test Case
        </Link>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Cases</p>
              <p className="text-3xl font-bold text-gray-800">{stats.totalTests}</p>
            </div>
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-indigo-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-emerald-600 font-medium">+12%</span>
            <span className="text-gray-600 ml-1">from last month</span>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Passed</p>
              <p className="text-3xl font-bold text-emerald-600">{stats.passedTests}</p>
            </div>
            <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-emerald-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-emerald-600 font-medium">{stats.passRate}%</span>
            <span className="text-gray-600 ml-1">success rate</span>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Failed</p>
              <p className="text-3xl font-bold text-red-600">{stats.failedTests}</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-red-600 font-medium">-5%</span>
            <span className="text-gray-600 ml-1">from last week</span>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-3xl font-bold text-blue-600">{stats.pendingTests}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-blue-600 font-medium">Active now</span>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <span className="font-medium text-gray-800">Filter Test Cases</span>
          </div>
          
          <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search test cases..."
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
              placeholder="All Statuses"
            />

            {/* Priority Filter */}
            <CustomDropdown
              options={priorityOptions}
              value={priorityFilter}
              onChange={setPriorityFilter}
              isOpen={priorityDropdownOpen}
              setIsOpen={setPriorityDropdownOpen}
              placeholder="All Priorities"
            />

            {/* Category Filter */}
            <CustomDropdown
              options={categoryOptions}
              value={categoryFilter}
              onChange={setCategoryFilter}
              isOpen={categoryDropdownOpen}
              setIsOpen={setCategoryDropdownOpen}
              placeholder="All Categories"
            />
          </div>
        </div>
      </div>

      {/* Test Cases List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">
            {filteredTestCases.length} of {testCases.length} test cases
          </h2>
        </div>

        <div className="space-y-3">
          {filteredTestCases.map((testCase: TestCase) => (
            <div key={testCase.id} className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200 hover:border-gray-300 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-800">{testCase.title}</h3>
                    <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-lg">{testCase.code}</span>
                    <span className={`text-xs font-medium px-2 py-1 rounded-lg border ${getPriorityColor(testCase.priority)}`}>
                      {testCase.priority}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-4">{testCase.goal}</p>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <Calendar className="w-4 h-4" />
                      <span>Created: {testCase.createdAt.toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>Last run: {testCase.lastRunAt ? testCase.lastRunAt.toLocaleDateString() : 'Never'}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-400">Runs:</span>
                      <span className="text-gray-600 font-medium">{testCase.totalRuns}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-400">Category:</span>
                      <span className="text-gray-600 font-medium">{testCase.category}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 ml-4">
                  <div className="flex items-center space-x-2">
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
                  
                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/test-details/${testCase.id}`}
                      className="inline-flex items-center px-3 py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
                    >
                      <FileText className="w-4 h-4 mr-1" />
                      View Details
                    </Link>
                    
                    <Link
                      to={`/history/${testCase.id}`}
                      className="inline-flex items-center px-3 py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
                    >
                      <Play className="w-4 h-4 mr-1" />
                      Run Test
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TestCases; 