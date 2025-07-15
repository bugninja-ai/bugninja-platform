import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Calendar, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Play, 
  Filter,
  Search,
  ArrowUpDown,
  MonitorPlay,
  Globe,
  Timer
} from 'lucide-react';
import { TestRun } from '../types';
import { mockApi } from '../data/mockData';

const STATUS_COLORS = {
  passed: 'text-green-600 bg-green-50 border-green-200',
  failed: 'text-red-600 bg-red-50 border-red-200',
  pending: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  skipped: 'text-gray-600 bg-gray-50 border-gray-200',
} as const;

export const TestHistory: React.FC = () => {
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<'date' | 'duration' | 'status'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    loadTestRuns();
  }, []);

  const loadTestRuns = async () => {
    try {
      setLoading(true);
      const runs = await mockApi.getTestRuns();
      setTestRuns(runs);
    } catch (error) {
      console.error('Failed to load test runs:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredAndSortedRuns = React.useMemo(() => {
    let filtered = testRuns.filter(run => {
      const matchesSearch = !searchTerm || 
        run.testCase.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        run.testCase.code.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = !statusFilter || run.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    });

    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'date':
          comparison = new Date(a.startedAt).getTime() - new Date(b.startedAt).getTime();
          break;
        case 'duration':
          comparison = a.duration - b.duration;
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
        default:
          comparison = 0;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [testRuns, searchTerm, statusFilter, sortBy, sortOrder]);

  const handleSort = (field: 'date' | 'duration' | 'status') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(date));
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading test history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Test Run History</h1>
          <p className="text-muted-foreground">Historical test execution results sorted by date</p>
        </div>

        {/* Filters and Search */}
        <div className="bg-card border border-border rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium text-foreground">Filter & Sort</span>
            </div>
            <span className="text-sm text-muted-foreground">
              {filteredAndSortedRuns.length} of {testRuns.length} runs
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search test runs..."
                className="w-full pl-10 pr-3 py-2 border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Status Filter */}
            <select
              className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="passed">Passed</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
              <option value="skipped">Skipped</option>
            </select>

            {/* Sort By */}
            <select
              className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'duration' | 'status')}
            >
              <option value="date">Sort by Date</option>
              <option value="duration">Sort by Duration</option>
              <option value="status">Sort by Status</option>
            </select>

            {/* Sort Order */}
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="flex items-center justify-center space-x-2 px-3 py-2 border border-input rounded-md bg-background text-foreground hover:bg-accent transition-colors"
            >
              <ArrowUpDown className="h-4 w-4" />
              <span>{sortOrder === 'asc' ? 'Ascending' : 'Descending'}</span>
            </button>
          </div>
        </div>

        {/* Test Runs List */}
        <div className="space-y-4">
          {filteredAndSortedRuns.length === 0 ? (
            <div className="bg-card border border-border rounded-lg p-8 text-center">
              <Play className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No test runs found</h3>
              <p className="text-muted-foreground">
                {searchTerm || statusFilter 
                  ? 'Try adjusting your filters to see more results.'
                  : 'Start running tests to see execution history here.'
                }
              </p>
            </div>
          ) : (
            filteredAndSortedRuns.map((run) => (
              <div key={run.id} className="bg-card border border-border rounded-lg p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <Link 
                        to={`/test-runs/${run.id}`}
                        className="text-lg font-semibold text-foreground hover:text-primary transition-colors"
                      >
                        {run.testCase.title}
                      </Link>
                      <span className="text-sm text-muted-foreground font-mono">{run.testCase.code}</span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${STATUS_COLORS[run.status]}`}>
                        {run.status === 'passed' && <CheckCircle className="h-3 w-3 mr-1" />}
                        {run.status === 'failed' && <XCircle className="h-3 w-3 mr-1" />}
                        {run.status === 'pending' && <Clock className="h-3 w-3 mr-1" />}
                        {run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                      </span>
                    </div>
                    
                    <p className="text-muted-foreground mb-3">{run.testCase.description}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="font-medium text-foreground">Started</p>
                          <p className="text-muted-foreground">{formatDate(run.startedAt)}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Timer className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="font-medium text-foreground">Duration</p>
                          <p className="text-muted-foreground">{formatDuration(run.duration)}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <MonitorPlay className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="font-medium text-foreground">Browser</p>
                          <p className="text-muted-foreground">{run.browser}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Globe className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="font-medium text-foreground">Environment</p>
                          <p className="text-muted-foreground capitalize">{run.environment}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="ml-4">
                    <Link
                      to={`/test-runs/${run.id}`}
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-primary bg-primary/10 hover:bg-primary/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
                    >
                      View Details
                    </Link>
                  </div>
                </div>

                {/* Test Results Summary */}
                <div className="border-t border-border pt-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-6">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-foreground">Steps:</span>
                        <span className="text-sm text-muted-foreground">{run.totalSteps} total</span>
                      </div>
                      
                      {run.passedSteps > 0 && (
                        <div className="flex items-center space-x-1">
                          <CheckCircle className="h-4 w-4 text-green-600" />
                          <span className="text-sm text-green-600 font-medium">{run.passedSteps} passed</span>
                        </div>
                      )}
                      
                      {run.failedSteps > 0 && (
                        <div className="flex items-center space-x-1">
                          <XCircle className="h-4 w-4 text-red-600" />
                          <span className="text-sm text-red-600 font-medium">{run.failedSteps} failed</span>
                        </div>
                      )}
                    </div>
                    
                    {run.completedAt && (
                      <div className="text-sm text-muted-foreground">
                        Completed: {formatDate(run.completedAt)}
                      </div>
                    )}
                  </div>
                  
                  {run.error && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm text-red-700 font-medium">Error:</p>
                      <p className="text-sm text-red-600">{run.error}</p>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Pagination placeholder */}
        {filteredAndSortedRuns.length > 10 && (
          <div className="mt-8 flex items-center justify-center">
            <div className="bg-card border border-border rounded-lg p-4">
              <p className="text-sm text-muted-foreground">
                Showing {Math.min(10, filteredAndSortedRuns.length)} of {filteredAndSortedRuns.length} runs
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}; 