import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Eye,
  Monitor
} from 'lucide-react';

interface TestRunTableViewProps {
  runs: any[]; // TODO: Create proper TestRun type
}

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

export const TestRunTableView: React.FC<TestRunTableViewProps> = ({ runs }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="text-left py-3 px-4 font-medium text-gray-900 text-sm">Test name</th>
              <th className="text-left py-3 px-4 font-medium text-gray-900 text-sm">Status</th>
              <th className="text-left py-3 px-4 font-medium text-gray-900 text-sm">Started at</th>
              <th className="text-left py-3 px-4 font-medium text-gray-900 text-sm">Duration</th>
              <th className="text-left py-3 px-4 font-medium text-gray-900 text-sm">Browser</th>
              <th className="text-left py-3 px-4 font-medium text-gray-900 text-sm">Environment</th>
              <th className="text-left py-3 px-4 font-medium text-gray-900 text-sm">Steps</th>
              <th className="text-right py-3 px-4 font-medium text-gray-900 text-sm">Actions</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => {
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
                <tr key={run.id} className="hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0">
                  {/* Test Name */}
                  <td className="py-4 px-4">
                    <div className="flex flex-col">
                      <Link 
                        to={`/runs/${run.id}`} 
                        className="font-medium text-gray-900 hover:text-indigo-600 transition-colors"
                      >
                        {run.test_case?.test_name || run.testCase?.title || `Test Run - ${run.id?.slice(-8)}`}
                      </Link>
                      <span className="text-sm text-gray-500 mt-1">{run.id}</span>
                    </div>
                  </td>

                  {/* Status */}
                  <td className="py-4 px-4">
                    <span className={`inline-flex items-center space-x-1 text-xs font-semibold px-2.5 py-1 rounded-full border ${getStatusColor(mappedStatus)}`}>
                      {getStatusIcon(mappedStatus)}
                      <span>{mappedStatus?.charAt(0).toUpperCase() + mappedStatus?.slice(1)}</span>
                    </span>
                  </td>

                  {/* Started At */}
                  <td className="py-4 px-4">
                    <div className="flex items-center text-sm text-gray-500">
                      <Calendar className="w-4 h-4 mr-1" />
                      <span>{startedAt.toLocaleDateString()}</span>
                    </div>
                  </td>

                  {/* Duration */}
                  <td className="py-4 px-4">
                    <div className="flex items-center text-sm text-gray-900">
                      <Clock className="w-4 h-4 mr-1 text-gray-400" />
                      {formatDuration(duration)}
                    </div>
                  </td>

                  {/* Browser */}
                  <td className="py-4 px-4">
                    <div className="flex flex-col">
                      <div className="flex items-center text-sm text-gray-900">
                        <Monitor className="w-4 h-4 mr-1 text-gray-400" />
                        {browserInfo.name}
                      </div>
                      <span className="text-xs text-gray-500 mt-1">{browserInfo.resolution}</span>
                    </div>
                  </td>

                  {/* Environment */}
                  <td className="py-4 px-4">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full border text-xs font-semibold bg-gray-100 text-gray-800 border-gray-200">
                      {run.origin === 'CI/CD' ? 'Production' : 'Development'}
                    </span>
                  </td>

                  {/* Steps */}
                  <td className="py-4 px-4">
                    {totalSteps > 0 ? (
                      <div className="flex items-center text-sm">
                        <span className="text-emerald-600 font-medium">{passedSteps}</span>
                        <span className="text-gray-400 mx-1">/</span>
                        <span className="text-red-600 font-medium">{failedSteps}</span>
                        <span className="text-gray-400 mx-1">/</span>
                        <span className="text-gray-900 font-medium">{totalSteps}</span>
                      </div>
                    ) : (
                      <span className="text-gray-400 text-sm">-</span>
                    )}
                  </td>

                  {/* Actions */}
                  <td className="py-4 px-4 text-right">
                    <Link
                      to={`/runs/${run.id}`}
                      className="inline-flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View details
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
