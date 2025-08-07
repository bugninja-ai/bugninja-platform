import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
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
  ArrowUp,
  ArrowDown,
  X
} from 'lucide-react';
import { CustomDropdown } from '../components/CustomDropdown';
import { useTestRuns } from '../hooks/useTestRuns';
import { useProjects } from '../hooks/useProjects';
import { TestCaseService } from '../services/testCaseService';
import { FrontendTestCase } from '../types';
import { Pagination } from '../shared/components/Pagination';



const TestRuns: React.FC = () => {
  // Get URL search parameters
  const [searchParams] = useSearchParams();
  
  // Get selected project
  const { selectedProject } = useProjects();
  
  // Dropdown states
  const [statusDropdownOpen, setStatusDropdownOpen] = useState(false);
  const [testCaseDropdownOpen, setTestCaseDropdownOpen] = useState(false);
  const [browserDropdownOpen, setBrowserDropdownOpen] = useState(false);

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
    setSortOrder,
    setTestCaseId,
    filters
  } = useTestRuns({
    projectId: selectedProject?.id,
    pageSize: 10
  });

  // Browser filtering state
  const [selectedBrowserId, setSelectedBrowserId] = useState<string | undefined>();

  // State for all test cases in the project (for dropdown options)
  const [allTestCases, setAllTestCases] = useState<FrontendTestCase[]>([]);
  const [testCasesLoading, setTestCasesLoading] = useState(false);

  // Handle URL query parameters on component mount
  useEffect(() => {
    const testCaseParam = searchParams.get('testCase');
    if (testCaseParam) {
      setTestCaseId(testCaseParam);
    }
  }, [searchParams, setTestCaseId]);

  // Fetch all test cases for the project (for dropdown options)
  useEffect(() => {
    const fetchAllTestCases = async () => {
      if (!selectedProject?.id) {
        return;
      }
      
      try {
        setTestCasesLoading(true);
        const response = await TestCaseService.getTestCases({
          project_id: selectedProject.id,
          page_size: 100 // Maximum allowed by backend
        });
        setAllTestCases(response.items);
      } catch (error) {
        console.error('Failed to fetch test cases for dropdown:', error);
        setAllTestCases([]);
      } finally {
        setTestCasesLoading(false);
      }
    };

    fetchAllTestCases();
  }, [selectedProject?.id]);

  // Apply client-side browser filtering (since backend doesn't support it)
  const filteredRuns = (testRuns || []).filter(run => {
    if (!selectedBrowserId) return true;
    const browserConfig = run.browser_config || run.browserConfig;
    return browserConfig?.id === selectedBrowserId;
  });

  // Calculate pagination for filtered results when browser filtering is applied
  const isBrowserFiltered = selectedBrowserId !== undefined;
  const currentPageSize = pageSize;
  const filteredTotalCount = filteredRuns.length;
  const filteredTotalPages = Math.ceil(filteredTotalCount / currentPageSize);
  const filteredCurrentPage = isBrowserFiltered ? 1 : page; // Reset to page 1 when filtering
  const filteredHasNext = isBrowserFiltered ? filteredCurrentPage < filteredTotalPages : hasNext;
  const filteredHasPrevious = isBrowserFiltered ? filteredCurrentPage > 1 : hasPrevious;

  // Use filtered pagination values when browser filtering is active
  const effectivePage = isBrowserFiltered ? filteredCurrentPage : page;
  const effectiveTotalPages = isBrowserFiltered ? filteredTotalPages : totalPages;
  const effectiveHasNext = isBrowserFiltered ? filteredHasNext : hasNext;
  const effectiveHasPrevious = isBrowserFiltered ? filteredHasPrevious : hasPrevious;

  // Apply pagination to filtered results when browser filtering is active
  const paginatedFilteredRuns = isBrowserFiltered 
    ? filteredRuns.slice((filteredCurrentPage - 1) * currentPageSize, filteredCurrentPage * currentPageSize)
    : filteredRuns;

  // Generate test case dropdown options - combine test cases from runs and all test cases
  const testCaseOptions = React.useMemo(() => {
    const testCaseMap = new Map<string, string>();
    
    // First, add test cases from current test runs (these are guaranteed to have runs)
    if (testRuns) {
      testRuns.forEach(run => {
        const testCaseId = run.test_case?.id || run.testCase?.id;
        const testCaseName = run.test_case?.test_name || run.testCase?.title;
        if (testCaseId && testCaseName) {
          testCaseMap.set(testCaseId, testCaseName);
        }
      });
    }
    
    // Then, add all test cases from the project (ensures we have all options)
    allTestCases.forEach(testCase => {
      if (testCase.id && testCase.title) {
        testCaseMap.set(testCase.id, testCase.title);
      }
    });
    
    return Array.from(testCaseMap.entries()).map(([id, name]) => ({ id, name }));
  }, [testRuns, allTestCases]);

  const browserOptions = React.useMemo(() => {
    if (!testRuns) return [];
    const browserConfigMap = new Map<string, string>();
    testRuns.forEach(run => {
      const browserConfig = run.browser_config || run.browserConfig;
      if (browserConfig) {
        const browserId = browserConfig.id;
        const userAgent = browserConfig.browser_config?.user_agent || browserConfig.userAgent;
        const viewport = browserConfig.browser_config?.viewport || browserConfig.viewport;
        let browserName = 'Unknown Browser';
        
        if (userAgent) {
          if (userAgent.includes('Chrome')) browserName = 'Chrome';
          else if (userAgent.includes('Firefox')) browserName = 'Firefox';
          else if (userAgent.includes('Safari')) browserName = 'Safari';
          else if (userAgent.includes('Edge')) browserName = 'Edge';
        }
        
        if (viewport) {
          browserName += ` (${viewport.width}x${viewport.height})`;
        }
        
        if (browserId) {
          browserConfigMap.set(browserId, browserName);
        }
      }
    });
    return Array.from(browserConfigMap.entries()).map(([id, name]) => ({ id, name }));
  }, [testRuns]);

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'finished':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-amber-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-amber-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
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
    // Extract browser info from browser_config
    const browserConfig = run.browser_config?.browser_config;
    const userAgent = browserConfig?.user_agent || '';
    const viewport = browserConfig?.viewport || { width: 0, height: 0 };
    
    // Determine browser name from user agent
    let browserName = 'Unknown Browser';
    if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
      browserName = 'Safari';
    } else if (userAgent.includes('Chrome')) {
      browserName = 'Chrome';
    } else if (userAgent.includes('Firefox')) {
      browserName = 'Firefox';
    } else if (userAgent.includes('Edge')) {
      browserName = 'Edge';
    }
    
    const resolution = viewport.width > 0 && viewport.height > 0 
      ? `${viewport.width}x${viewport.height}` 
      : 'Unknown resolution';
    
    return {
      name: browserName,
      resolution: resolution
    };
  };

  const statusOptions = [
    { value: 'all', label: 'All statuses' },
    { value: 'FINISHED', label: 'Finished' },
    { value: 'FAILED', label: 'Failed' },
    { value: 'PENDING', label: 'Pending' },
  ];

  // Format options for dropdowns
  const testCaseDropdownOptions = React.useMemo(() => {
    return [
      { value: 'all', label: 'All test cases' },
      ...testCaseOptions.map(testCase => ({
        value: testCase.id,
        label: testCase.name
      }))
    ];
  }, [testCaseOptions]);

  const browserDropdownOptions = [
    { value: 'all', label: 'All browsers' },
    ...browserOptions.map(browserConfig => ({
      value: browserConfig.id,
      label: browserConfig.name
    }))
  ];





  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Test runs</h1>
          <p className="mt-1 text-gray-600">
            {filters.testCaseId ? (
              <>Runs for test case: <span className="font-medium">{testCaseOptions.find(tc => tc.id === filters.testCaseId)?.name || filters.testCaseId}</span></>
            ) : (
              'View and analyze past test run results'
            )}
          </p>
        </div>
        <div className="mt-4 sm:mt-0 text-sm text-gray-500">
          {isBrowserFiltered ? (
            `Showing ${paginatedFilteredRuns.length} of ${filteredTotalCount} filtered test runs`
          ) : (
            `Showing ${((page - 1) * pageSize) + 1}-${Math.min(page * pageSize, totalCount)} of ${totalCount} test runs`
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total runs</p>
              <p className="text-3xl font-bold text-gray-800">
                {isBrowserFiltered ? filteredTotalCount : totalCount}
              </p>
            </div>
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
              <Play className="w-6 h-6 text-indigo-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-indigo-600 font-medium">
              {isBrowserFiltered ? 'Filtered results' : 'Last 30 days'}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success rate</p>
              <p className="text-3xl font-bold text-emerald-600">
                {(() => {
                  const runsToCheck = isBrowserFiltered ? filteredRuns : testRuns;
                  return runsToCheck && runsToCheck.length > 0 
                    ? Math.round((runsToCheck.filter(r => r.current_state === 'FINISHED').length / runsToCheck.length) * 100)
                    : 0;
                })()}%
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
                {(() => {
                  const runsToCheck = isBrowserFiltered ? filteredRuns : testRuns;
                  return runsToCheck && runsToCheck.length > 0 
                    ? formatDuration(runsToCheck.reduce((acc: number, run: any) => acc + (run.duration || 0), 0) / runsToCheck.length)
                    : '0s';
                })()}
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
            <Filter className="w-5 h-5 text-gray-400" />
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

            {/* Sort by Date Toggle */}
            <button
              onClick={() => setSortOrder(filters.sortOrder === 'desc' ? 'asc' : 'desc')}
              className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              title={`Sort by date ${filters.sortOrder === 'desc' ? 'ascending' : 'descending'}`}
            >
              <Calendar className="w-4 h-4 text-gray-400" />
              {filters.sortOrder === 'desc' ? (
                <ArrowDown className="w-3 h-3 ml-1 text-gray-500" />
              ) : (
                <ArrowUp className="w-3 h-3 ml-1 text-gray-500" />
              )}
            </button>

            {/* Test Case Filter */}
            <CustomDropdown
              options={testCaseDropdownOptions}
              value={filters.testCaseId || 'all'}
              onChange={(value) => setTestCaseId(value === 'all' ? undefined : value)}
              isOpen={testCaseDropdownOpen}
              setIsOpen={setTestCaseDropdownOpen}
              placeholder="All test cases"
              dropdownClassName="!left-0 !right-auto w-72"
            />

            {/* Browser/Viewport Filter */}
            <CustomDropdown
              options={browserDropdownOptions}
              value={selectedBrowserId || 'all'}
              onChange={(value) => setSelectedBrowserId(value === 'all' ? undefined : value)}
              isOpen={browserDropdownOpen}
              setIsOpen={setBrowserDropdownOpen}
              placeholder="All browsers"
              dropdownClassName="!left-0 !right-auto w-56"
            />

            {/* Status Filter */}
            <CustomDropdown
              options={statusOptions}
              value={filters.status || 'all'}
              onChange={(value) => setStatus(value === 'all' ? undefined : value)}
              isOpen={statusDropdownOpen}
              setIsOpen={setStatusDropdownOpen}
              placeholder="All statuses"
            />

            {/* Remove All Filters Button */}
            {(filters.search || filters.status || filters.testCaseId || selectedBrowserId) && (
              <button
                onClick={() => {
                  setSearch('');
                  setStatus(undefined);
                  setTestCaseId(undefined);
                  setSelectedBrowserId(undefined);
                }}
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                title="Clear all filters"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            )}
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
            <AlertCircle className="w-8 h-8 mx-auto mb-4 text-gray-400" />
            <p className="text-red-600 mb-4">{testRunsError}</p>
            <button
              onClick={() => refetch()}
              className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </button>
          </div>
        ) : paginatedFilteredRuns.length === 0 ? (
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
            {paginatedFilteredRuns.map((run: any) => {
              const browserInfo = getBrowserInfo(run);
              const startedAt = new Date(run.started_at || run.startedAt || run.created_at);
              
              // Calculate duration from start/finish times if available
              let duration = run.duration || 0;
              if (run.finished_at && run.started_at && duration === 0) {
                duration = (new Date(run.finished_at).getTime() - new Date(run.started_at).getTime()) / 1000;
              }
              
              const passedSteps = run.passed_steps || run.passedSteps || 0;
              const failedSteps = run.failed_steps || run.failedSteps || 0;
              const totalSteps = run.total_steps || run.totalSteps || passedSteps + failedSteps;
              
              // Map backend status to frontend status
              const statusMap: { [key: string]: string } = {
                'PASSED': 'finished',
                'FAILED': 'failed',
                'PENDING': 'pending',
                'RUNNING': 'pending',
                'FINISHED': 'finished',
                'ERROR': 'failed'
              };
              const mappedStatus = statusMap[run.current_state] || 'pending';
              
              return (
                <div key={run.id} className="bg-white rounded-lg p-6 border border-gray-200 hover:border-gray-300 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-800">
                          {run.test_case?.test_name || run.testCase?.title || `Test Run - ${run.id?.slice(-8)}`}
                        </h3>
                        <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-lg">
                          {run.id || 'N/A'}
                        </span>
                        <span className={`inline-flex items-center space-x-1 text-xs font-semibold px-2.5 py-1 rounded-full border ${getStatusColor(mappedStatus)}`}>
                          {getStatusIcon(mappedStatus)}
                          <span>{mappedStatus?.charAt(0).toUpperCase() + mappedStatus?.slice(1)}</span>
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
                          <span className="text-gray-600 font-medium">{run.origin === 'CI/CD' ? 'Production' : 'Development'}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 ml-4">
                      <Link
                        to={`/runs/${run.id}`}
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
              currentPage={effectivePage}
              totalPages={effectiveTotalPages}
              onPageChange={isBrowserFiltered ? () => {} : setPage} // Disable pagination when browser filtering
              hasNext={effectiveHasNext}
              hasPrevious={effectiveHasPrevious}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default TestRuns; 