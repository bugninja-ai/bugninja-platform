import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Target,
  Calendar,
  Timer,
  MonitorPlay,
  Globe,
  AlertTriangle,
  ChevronRight,
  Play
} from 'lucide-react';
import { TestRun } from '../types';
import { mockApi } from '../data/mockData';

const STATUS_COLORS = {
  passed: 'text-green-600 bg-green-50 border-green-200',
  failed: 'text-red-600 bg-red-50 border-red-200',
  pending: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  skipped: 'text-gray-600 bg-gray-50 border-gray-200',
} as const;

export const TestRunDetail: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const [testRun, setTestRun] = useState<TestRun | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (runId) {
      loadTestRun(runId);
    }
  }, [runId]);

  const loadTestRun = async (id: string) => {
    try {
      setLoading(true);
      const run = await mockApi.getTestRun(id);
      setTestRun(run);
    } catch (error) {
      console.error('Failed to load test run:', error);
    } finally {
      setLoading(false);
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
          <p className="text-muted-foreground">Loading test run details...</p>
        </div>
      </div>
    );
  }

  if (!testRun) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">Test run not found</h3>
          <p className="text-muted-foreground mb-4">The requested test run could not be found.</p>
          <Link
            to="/reports"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary bg-primary/10 hover:bg-primary/20 transition-colors"
          >
            Back to Reports
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-6">
          <Link to="/reports" className="hover:text-foreground transition-colors">
            Test Reports
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-foreground">Test Run Details</span>
        </div>

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <h1 className="text-3xl font-bold text-foreground">{testRun.testCase.title}</h1>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${STATUS_COLORS[testRun.status]}`}>
                {testRun.status === 'passed' && <CheckCircle className="h-4 w-4 mr-2" />}
                {testRun.status === 'failed' && <XCircle className="h-4 w-4 mr-2" />}
                {testRun.status === 'pending' && <Clock className="h-4 w-4 mr-2" />}
                {testRun.status.toUpperCase()}
              </span>
              <span className="text-sm text-muted-foreground font-mono">{testRun.testCase.code}</span>
            </div>
            <p className="text-muted-foreground mb-4">{testRun.testCase.description}</p>
            
            {/* Test Goal */}
            <div className="bg-muted/50 rounded-md p-3 mb-4 max-w-2xl">
              <div className="flex items-center space-x-2 mb-1">
                <Target className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium text-foreground">Goal:</span>
              </div>
              <p className="text-sm text-muted-foreground">{testRun.testCase.goal}</p>
            </div>
          </div>

          <Link
            to="/reports"
            className="inline-flex items-center px-4 py-2 border border-border rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Reports
          </Link>
        </div>

        {/* Run Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium text-foreground">Last Run</span>
            </div>
            <p className="text-sm text-muted-foreground">{formatDate(testRun.startedAt)}</p>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Timer className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium text-foreground">Duration</span>
            </div>
            <p className="text-sm text-muted-foreground">{formatDuration(testRun.duration)}</p>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-foreground">Passed Steps</span>
            </div>
            <p className="text-sm text-green-600 font-semibold">{testRun.passedSteps}/{testRun.totalSteps}</p>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <XCircle className="h-4 w-4 text-red-600" />
              <span className="text-sm font-medium text-foreground">Failed Steps</span>
            </div>
            <p className="text-sm text-red-600 font-semibold">{testRun.failedSteps}/{testRun.totalSteps}</p>
          </div>
        </div>

        {/* Environment Information */}
        <div className="bg-card border border-border rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-foreground mb-4">Environment Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center space-x-3">
              <MonitorPlay className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium text-foreground">Browser</p>
                <p className="text-sm text-muted-foreground">{testRun.browser}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Globe className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium text-foreground">Environment</p>
                <p className="text-sm text-muted-foreground capitalize">{testRun.environment}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Play className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium text-foreground">User Agent</p>
                <p className="text-sm text-muted-foreground truncate">{testRun.userAgent}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Test Execution Steps */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-lg font-semibold text-foreground mb-6">Test Execution Steps</h2>
          
          <div className="space-y-6">
            {testRun.steps.map((step) => (
              <div key={step.id} className="border border-border rounded-lg overflow-hidden">
                <div className="flex items-center justify-between p-4 bg-muted/20">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted text-sm font-medium text-foreground">
                      {step.stepNumber}
                    </div>
                    <h3 className="font-medium text-foreground">{step.description}</h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${STATUS_COLORS[step.status]}`}>
                      {step.status === 'passed' && <CheckCircle className="h-3 w-3 mr-1" />}
                      {step.status === 'failed' && <XCircle className="h-3 w-3 mr-1" />}
                      {step.status.charAt(0).toUpperCase() + step.status.slice(1)}
                    </span>
                  </div>
                  
                  <div className="text-sm text-muted-foreground">
                    Duration: {formatDuration(step.duration)}
                  </div>
                </div>
                
                <div className="p-4 space-y-4">
                  {/* Expected Result */}
                  <div>
                    <p className="text-sm font-medium text-foreground mb-2">Expected:</p>
                    <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                      <p className="text-sm text-blue-800">{step.expected}</p>
                    </div>
                  </div>
                  
                  {/* Actual Result */}
                  <div>
                    <p className="text-sm font-medium text-foreground mb-2">Actual:</p>
                    <div className={`border rounded-md p-3 ${
                      step.status === 'passed' 
                        ? 'bg-green-50 border-green-200' 
                        : step.status === 'failed'
                        ? 'bg-red-50 border-red-200'
                        : 'bg-gray-50 border-gray-200'
                    }`}>
                      <p className={`text-sm ${
                        step.status === 'passed' 
                          ? 'text-green-800' 
                          : step.status === 'failed'
                          ? 'text-red-800'
                          : 'text-gray-800'
                      }`}>
                        {step.actual}
                      </p>
                    </div>
                  </div>
                  
                  {/* Error Details */}
                  {step.error && (
                    <div>
                      <p className="text-sm font-medium text-foreground mb-2">Error Details:</p>
                      <div className="bg-red-50 border border-red-200 rounded-md p-3">
                        <p className="text-sm text-red-800">{step.error}</p>
                      </div>
                    </div>
                  )}
                  
                  {/* Screenshot placeholder */}
                  {step.screenshot && (
                    <div>
                      <p className="text-sm font-medium text-foreground mb-2">Screenshot:</p>
                      <div className="bg-gray-100 border border-gray-200 rounded-md p-8 text-center">
                        <p className="text-sm text-gray-600">Screenshot: {step.screenshot}</p>
                        <p className="text-xs text-gray-500 mt-1">Screenshot viewing functionality would be implemented here</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          {testRun.steps.length === 0 && (
            <div className="text-center py-8">
              <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No execution steps</h3>
              <p className="text-muted-foreground">This test run hasn't been executed yet or has no recorded steps.</p>
            </div>
          )}
        </div>

        {/* Global Error */}
        {testRun.error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Test Run Error</h3>
                <p className="text-sm text-red-700 mt-1">{testRun.error}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}; 