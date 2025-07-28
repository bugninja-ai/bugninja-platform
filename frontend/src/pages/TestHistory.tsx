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
  Monitor,
  Loader2,
  RefreshCw,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { TestRun } from '../types';
import { CustomDropdown } from '../components/CustomDropdown';
import { useTestRuns } from '../hooks/useTestRuns';

// Pagination Component
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  hasNext: boolean;
  hasPrevious: boolean;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  hasNext,
  hasPrevious,
}) => {
  if (totalPages <= 1) return null;

  const getVisiblePages = () => {
    const pages: (number | string)[] = [];
    const showPages = 5; // Show 5 page numbers at most

    if (totalPages <= showPages) {
      // If total pages is small, show all
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);

      let startPage = Math.max(2, currentPage - 1);
      let endPage = Math.min(totalPages - 1, currentPage + 1);

      // Adjust range if we're near the beginning or end
      if (currentPage <= 3) {
        endPage = 4;
      } else if (currentPage >= totalPages - 2) {
        startPage = totalPages - 3;
      }

      // Add ellipsis if there's a gap after page 1
      if (startPage > 2) {
        pages.push('...');
      }

      // Add visible page numbers
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }

      // Add ellipsis if there's a gap before last page
      if (endPage < totalPages - 1) {
        pages.push('...');
      }

      // Always show last page
      if (totalPages > 1) {
        pages.push(totalPages);
      }
    }

    return pages;
  };

  return (
    <div className="flex items-center justify-center space-x-2 mt-8">
      {/* Previous button */}
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={!hasPrevious}
        className="flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:text-gray-500"
      >
        <ChevronLeft className="w-4 h-4 mr-1" />
        Previous
      </button>

      {/* Page numbers */}
      <div className="flex items-center space-x-1">
        {getVisiblePages().map((page, index) => (
          <React.Fragment key={index}>
            {page === '...' ? (
              <span className="px-3 py-2 text-sm text-gray-400">...</span>
            ) : (
              <button
                onClick={() => onPageChange(page as number)}
                className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  currentPage === page
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                }`}
              >
                {page}
              </button>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Next button */}
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={!hasNext}
        className="flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:text-gray-500"
      >
        Next
        <ChevronRight className="w-4 h-4 ml-1" />
      </button>
    </div>
  );
};

const TestHistory: React.FC = () => {
  // Dropdown states
  const [statusDropdownOpen, setStatusDropdownOpen] = useState(false);

  // Use the test runs hook
  const {
    data: testRuns,
    loading: testRunsLoading,
    error: testRunsError,
    totalCount,
    page,
    pageSize,
    totalPages,
    hasNext,
    hasPrevious,
    refetch,
    setPage,
    setSearch,
    setStatus,
    filters
  } = useTestRuns({
    pageSize: 15
  });

  // testRuns are already filtered by the hook
  const filteredRuns = testRuns || [];

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

  const getBrowserInfo = (run: any) => {
    // For API data, we'll get browser info from the run itself
    return {
      name: run.browser || 'Unknown Browser',
      resolution: run.resolution || 'Unknown resolution'
    };
  };

  const statusOptions = [
    { value: 'all', label: 'All statuses' },
    { value: 'passed', label: 'Passed' },
    { value: 'failed', label: 'Failed' },
    { value: 'pending', label: 'Pending' },
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
          Showing {((page - 1) * pageSize) + 1}-{Math.min(page * pageSize, totalCount)} of {totalCount} test runs
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total runs</p>
              <p className="text-3xl font-bold text-gray-800">{totalCount}</p>
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
                {testRuns && testRuns.length > 0 
                  ? Math.round((testRuns.filter(r => r.status === 'passed').length / testRuns.length) * 100)
                  : 0}%
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
                {testRuns && testRuns.length > 0 
                  ? formatDuration(testRuns.reduce((acc: number, run: any) => acc + (run.duration || 0), 0) / testRuns.length)
                  : '0s'}
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
                value={filters.search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 pr-4 py-2 w-full sm:w-64 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
              />
            </div>

            {/* Status Filter */}
            <CustomDropdown
              options={statusOptions}
              value={filters.status || 'all'}
              onChange={(value) => setStatus(value === 'all' ? undefined : value)}
              isOpen={statusDropdownOpen}
              setIsOpen={setStatusDropdownOpen}
              placeholder="All statuses"
            />
          </div>
        </div>
      </div>

      {/* Test Runs List */}
      <div className="space-y-3">
        {testRunsLoading ? (
          <div className="bg-white rounded-lg p-8 border border-gray-200 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-gray-400" />
            <p className="text-gray-600">Loading test runs...</p>
          </div>
        ) : testRunsError ? (
          <div className="bg-white rounded-lg p-8 border border-gray-200 text-center">
            <AlertCircle className="w-8 h-8 mx-auto mb-4 text-red-500" />
            <p className="text-red-600 mb-4">{testRunsError}</p>
            <button
              onClick={() => refetch()}
              className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </button>
          </div>
        ) : filteredRuns.length === 0 ? (
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
        ) : (
          <>
            {filteredRuns.map((run: any) => {
              const browserInfo = getBrowserInfo(run);
              const startedAt = new Date(run.started_at || run.startedAt || run.created_at);
              const duration = run.duration || 0;
              const passedSteps = run.passed_steps || run.passedSteps || 0;
              const failedSteps = run.failed_steps || run.failedSteps || 0;
              const totalSteps = run.total_steps || run.totalSteps || passedSteps + failedSteps;
              
              return (
                <div key={run.id} className="bg-white rounded-lg p-6 border border-gray-200 hover:border-gray-300 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-800">
                          {run.test_case?.test_name || run.testCase?.title || 'Unknown Test Case'}
                        </h3>
                        <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-lg">
                          {run.test_case?.id?.slice(-8) || run.id?.slice(-8) || 'N/A'}
                        </span>
                        <span className={`inline-flex items-center text-xs font-medium px-2 py-1 rounded-lg border ${getStatusColor(run.status)}`}>
                          {getStatusIcon(run.status)}
                          <span className="ml-1">{run.status?.charAt(0).toUpperCase() + run.status?.slice(1) || 'Unknown'}</span>
                        </span>
                      </div>
                      
                      <p className="text-gray-600 mb-3">
                        {run.test_case?.test_description || run.testCase?.description || 'No description available'}
                      </p>

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
                          <span>Started: {startedAt.toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="w-4 h-4" />
                          <span>Duration: {formatDuration(duration)}</span>
                        </div>
                        {totalSteps > 0 && (
                          <div className="flex items-center space-x-1">
                            <span className="text-gray-400">Steps:</span>
                            <span className="text-emerald-600 font-medium">{passedSteps}</span>
                            <span className="text-gray-400">/</span>
                            <span className="text-red-600 font-medium">{failedSteps}</span>
                            <span className="text-gray-400">/</span>
                            <span className="font-medium">{totalSteps}</span>
                          </div>
                        )}
                        <div className="flex items-center space-x-1">
                          <span className="text-gray-400">Environment:</span>
                          <span className="text-gray-600 font-medium">{run.environment || 'Production'}</span>
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

            {/* Pagination */}
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={setPage}
              hasNext={hasNext}
              hasPrevious={hasPrevious}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default TestHistory; 