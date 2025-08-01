import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Target,
  Calendar,
  Timer,
  MonitorPlay,
  Globe,
  AlertTriangle,
  Play,
  FileText,
  Brain,
  Image,
  MousePointer,
  Edit,
  Lock,
  User,
  Search,
  ArrowLeft,
  ZoomIn
} from 'lucide-react';
import { TestRun, BrainState } from '../types';
import { TestCaseService } from '../services/testCaseService';
import { BASE_DOMAIN } from '../services/api';
import ScreenshotModal from '../components/ScreenshotModal';

const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'passed':
    case 'finished':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    case 'failed':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'pending':
      return 'bg-amber-100 text-amber-800 border-amber-200';
    case 'skipped':
      return 'bg-gray-100 text-gray-800 border-gray-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getStatusIcon = (status: string) => {
  switch (status.toLowerCase()) {
    case 'passed':
    case 'finished':
      return <CheckCircle className="w-4 h-4 text-emerald-500" />;
    case 'failed':
      return <XCircle className="w-4 h-4 text-red-500" />;
    case 'pending':
      return <Clock className="w-4 h-4 text-amber-500" />;
    default:
      return <Clock className="w-4 h-4 text-amber-500" />;
  }
};

export const TestRunDetail: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const [testRun, setTestRun] = useState<TestRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedScreenshot, setSelectedScreenshot] = useState<string>('');
  const [selectedActionData, setSelectedActionData] = useState<any>(null);

  useEffect(() => {
    if (runId) {
      loadTestRun(runId);
    }
  }, [runId]);

  const transformBackendTestRun = (backendData: any): TestRun => {
    // Map status from current_state
    const statusMap: { [key: string]: 'passed' | 'failed' | 'pending' } = {
      'PASSED': 'passed',
      'FAILED': 'failed',
      'PENDING': 'pending',
      'RUNNING': 'pending',
      'FINISHED': 'passed', // Assuming FINISHED means successful completion
      'ERROR': 'failed'
    };

    // Extract browser information
    const browserConfig = backendData.browser_config?.browser_config;
    const userAgent = browserConfig?.user_agent || '';
    const viewport = browserConfig?.viewport || { width: 1920, height: 1080 };
    
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

    // Transform brain states to steps
    const steps = backendData.brain_states?.map((brainState: any, index: number) => {
      // Get the first history element for basic step info
      const firstHistoryElement = brainState.history_elements?.[0];
      
      // Determine step status based on history elements
      const hasFailedElement = brainState.history_elements?.some((he: any) => he.history_element_state === 'FAILED');
      const stepStatus = hasFailedElement ? 'failed' : 'passed';
      
      // Transform history elements to actions
      const actions = brainState.history_elements?.map((historyElement: any) => {
        const action = historyElement.action;
        let actionType = 'Unknown Action';
        let actionDetails: any = {};
        
        // Determine action type from the action object
        if (action.go_to_url) {
          actionType = 'Navigate to URL';
          actionDetails.url = action.go_to_url.url;
        } else if (action.input_text) {
          actionType = 'Fill text input';
          let inputText = action.input_text.text;
          
          // Handle secrets - extract secret name and mark as secret
          const secretMatch = inputText.match(/<secret>([^<]+)<\/secret>/);
          if (secretMatch) {
            const secretName = secretMatch[1];
            actionDetails.inputText = secretName;
            actionDetails.isSecret = true;
            actionType = 'Fill password/secret input';
          } else {
            actionDetails.inputText = inputText;
            actionDetails.isSecret = false;
          }
          
          actionDetails.xpath = historyElement.dom_element_data?.xpath;
        } else if (action.click_element_by_index) {
          actionType = 'Click element';
          actionDetails.xpath = historyElement.dom_element_data?.xpath;
        } else if (action.done) {
          actionType = 'Test completed';
          actionDetails.resultMessage = action.done.text;
        }
        
        return {
          id: historyElement.id,
          actionType,
          status: historyElement.history_element_state === 'FAILED' ? 'failed' : 'passed',
          screenshot: historyElement.screenshot || null,
          xpath: actionDetails.xpath,
          url: actionDetails.url,
          inputText: actionDetails.inputText,
          resultMessage: actionDetails.resultMessage,

          isSecret: actionDetails.isSecret,
          evaluatePreviousGoal: brainState.evaluation_previous_goal,
          nextGoal: brainState.next_goal,
          memory: brainState.memory
        };
      }) || [];

      return {
        id: brainState.id,
        stepNumber: index + 1,
        description: brainState.next_goal || `Step ${index + 1}`,
        status: stepStatus,
        duration: 0, // Not provided in backend data
        brainState: {
          id: brainState.id,
          evaluatePreviousGoal: brainState.evaluation_previous_goal,
          nextGoal: brainState.next_goal,
          memory: brainState.memory,
          actions
        }
      };
    }) || [];

    // Calculate totals
    const totalSteps = steps.length;
    const passedSteps = steps.filter(step => step.status === 'passed').length;
    const failedSteps = steps.filter(step => step.status === 'failed').length;

    // Use real test case data from backend if available
    const realTestCase = backendData.test_case;
    const testCase = {
      id: realTestCase?.id || backendData.test_traversal_id,
      code: realTestCase?.id ? `TC-${realTestCase.id.slice(-8)}` : `TR-${backendData.id.slice(-8)}`,
      title: realTestCase?.test_name || `Test Run - ${backendData.id.slice(-8)}`,
      description: realTestCase?.test_description || 'Automated test execution',
      goal: realTestCase?.test_goal || 'Execute test case objectives',
      browserConfigs: [{
        id: backendData.browser_config?.id || 'unknown',
        name: `${browserName} - ${viewport.width}x${viewport.height}`,
        userAgent: userAgent,
        viewport: viewport,
        geolocation: browserConfig?.geolocation,
        timeout: browserConfig?.timeout
      }]
    };

    // Calculate duration if we have both start and finish times
    let duration = 0;
    if (backendData.finished_at && backendData.started_at) {
      duration = (new Date(backendData.finished_at).getTime() - new Date(backendData.started_at).getTime()) / 1000;
    }

    return {
      id: backendData.id,
      testCase,
      status: statusMap[backendData.current_state] || 'pending',
      startedAt: new Date(backendData.started_at),
      finishedAt: backendData.finished_at ? new Date(backendData.finished_at) : undefined,
      duration: duration,
      environment: backendData.origin === 'CI/CD' ? 'production' : 'development',
      browser: browserName,
      userAgent: userAgent,
      totalSteps,
      passedSteps,
      failedSteps,
      steps,
      gif: backendData.run_gif || null
    };
  };

  const loadTestRun = async (id: string) => {
    try {
      setLoading(true);
      const backendData = await TestCaseService.getTestRun(id);
      const transformedRun = transformBackendTestRun(backendData);
      setTestRun(transformedRun);
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

  const getActionIcon = (actionType: string, iconName?: string) => {
    const iconMap: { [key: string]: React.ComponentType<any> } = {
      // Legacy action types
      'go_to_url': Globe,
      'click_element_by_index': MousePointer,
      'input_text': Edit,
      'wait': Clock,
      'search_google': Search,
      // New proper action names
      'Navigate to URL': Globe,
      'Fill text input': Edit,
      'Fill password input': Lock,
      'Fill password/secret input': Lock,
      'Click login button': MousePointer,
      'Click element': MousePointer,
      'Wait for page load': Clock,
      'Close popup dialog': XCircle,
      'Click user profile': User,
      'Wait for menu': Clock,
      'Search for settings': Search,
      'Test completed': CheckCircle,
      // Icon name mappings
      'globe': Globe,
      'edit': Edit,
      'lock': Lock,
      'mouse-pointer': MousePointer,
      'clock': Clock,
      'x': XCircle,
      'user': User,
      'search': Search
    };
    
    const IconComponent = iconMap[iconName || actionType] || Play;
    return <IconComponent className="w-4 h-4 text-indigo-600" />;
  };

  const getBrowserInfo = (run: TestRun) => {
    const browserConfig = run.testCase.browserConfigs.find(config => 
      config.userAgent === run.userAgent || 
      config.name.toLowerCase().includes(run.browser.toLowerCase().split(' ')[0])
    );
    
    if (browserConfig) {
      return browserConfig;
    }
    
    return {
      id: 'default',
      name: run.browser,
      userAgent: run.userAgent,
      viewport: { width: 1920, height: 1080 }
    };
  };

  const handleScreenshotClick = (screenshot: string, actionData: any) => {
    setSelectedScreenshot(screenshot);
    setSelectedActionData(actionData);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedScreenshot('');
    setSelectedActionData(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading test run details...</p>
        </div>
      </div>
    );
  }

  if (!testRun) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-800 mb-2">Test run not found</h3>
          <p className="text-gray-600 mb-4">The requested test run could not be found.</p>
          <Link
            to="/runs"
            className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Back to test runs
          </Link>
        </div>
      </div>
    );
  }

  const browserInfo = getBrowserInfo(testRun);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h1 className="text-3xl font-bold text-gray-800">{testRun.testCase.title}</h1>
            <span className={`inline-flex items-center space-x-1 text-xs font-semibold px-2.5 py-1 rounded-full border ${getStatusColor(testRun.status)}`}>
              {getStatusIcon(testRun.status)}
              <span>{testRun.status.toUpperCase()}</span>
            </span>
            <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-lg">{testRun.id || 'N/A'}</span>
          </div>
          <p className="text-gray-600 mb-4">{testRun.testCase.description}</p>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to="/runs"
            className="inline-flex items-center px-3 py-2 text-sm font-medium border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to test runs
          </Link>
          
          <Link
            to={`/test-details/${testRun.testCase.id}`}
            className="inline-flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
          >
            <FileText className="w-4 h-4 mr-1" />
            View test case
          </Link>
        </div>
      </div>

      {/* Test Goal */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200 mt-8 mb-6">
        <div className="flex items-center space-x-2 mb-4">
          <Target className="h-5 w-5 text-blue-600" />
          <span className="text-lg font-semibold text-gray-800">Test goal</span>
        </div>
        <p className="text-gray-600">{testRun.testCase.goal}</p>
      </div>

      {/* Test Run GIF */}
      {testRun.gif && (
        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200 mb-6">
          <div className="flex items-center space-x-2 mb-4">
            <MonitorPlay className="h-5 w-5 text-indigo-600" />
            <span className="text-lg font-semibold text-gray-800">Test execution recording</span>
          </div>
          <div className="flex justify-center">
            <div className="bg-gray-100 border border-gray-200 rounded-lg overflow-hidden max-w-4xl w-full">
              <img
                src={`${BASE_DOMAIN}/${testRun.gif}`}
                alt="Test execution recording"
                className="w-full h-auto"
                style={{ maxHeight: '600px', objectFit: 'contain' }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Run Information */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Run information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Last run</span>
            </div>
            <p className="text-gray-800">{formatDate(testRun.startedAt)}</p>
          </div>

          <div>
            <div className="flex items-center space-x-2 mb-2">
              <Timer className="h-4 w-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Duration</span>
            </div>
            <p className="text-gray-800">{formatDuration(testRun.duration)}</p>
          </div>

          <div>
            <div className="flex items-center space-x-2 mb-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-gray-700">Passed steps</span>
            </div>
            <p className="text-green-600 font-semibold">{testRun.passedSteps}/{testRun.totalSteps}</p>
          </div>

          <div>
            <div className="flex items-center space-x-2 mb-2">
              <XCircle className="h-4 w-4 text-red-600" />
              <span className="text-sm font-medium text-gray-700">Failed steps</span>
            </div>
            <p className="text-red-600 font-semibold">{testRun.failedSteps}/{testRun.totalSteps}</p>
          </div>
        </div>
      </div>

      {/* Browser Configuration */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Browser configuration</h2>
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-3">
            <MonitorPlay className="w-5 h-5 text-gray-600" />
            <h3 className="font-medium text-gray-800">{browserInfo.name}</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">User agent</label>
              <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded text-gray-700 text-xs break-all">
                {browserInfo.userAgent}
              </div>
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Viewport</label>
              <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded text-gray-700">
                {browserInfo.viewport.width} × {browserInfo.viewport.height}
              </div>
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Environment</label>
              <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded text-gray-700 capitalize">
                {testRun.environment}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Test Execution Steps */}
      <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-6">Test execution steps</h2>
        
        <div className="space-y-6">
          {testRun.steps.map((step) => (
            <div key={step.id} className="border border-gray-200 rounded-lg overflow-hidden">
              <div className="flex items-center justify-between p-4 bg-gray-50">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-white border border-gray-200 text-sm font-medium text-gray-700">
                    {step.stepNumber}
                  </div>
                  <h3 className="font-medium text-gray-800">{step.description}</h3>
                  <span className={`inline-flex items-center space-x-1 text-xs font-semibold px-2.5 py-1 rounded-full border ${getStatusColor(step.status)}`}>
                    {getStatusIcon(step.status)}
                    <span>{step.status.charAt(0).toUpperCase() + step.status.slice(1)}</span>
                  </span>
                </div>
                
                <div className="text-sm text-gray-600">
                  Duration: {formatDuration(step.duration)}
                </div>
              </div>
              
              <div className="p-4 space-y-4">
                {/* Brain State with Multiple Actions */}
                {step.brainState && (
                  <>
                    {/* Brain State Section (Purple) */}
                    <div className="bg-purple-50 border border-purple-200 rounded-lg overflow-hidden mb-4">
                      <div className="flex items-center justify-between p-3 bg-purple-100/50">
                        <div className="flex items-center space-x-2">
                          <Brain className="h-4 w-4 text-purple-600" />
                          <span className="text-sm font-semibold text-gray-800">AI brain state</span>
                        </div>
                      </div>
                      
                      <div className="p-4 space-y-3">
                        <div>
                          <p className="text-xs font-medium text-purple-700 mb-1">Evaluate previous goal:</p>
                          <div className="text-sm text-purple-800 bg-white/70 border border-purple-200 rounded p-2">
                            {step.brainState.actions[0]?.evaluatePreviousGoal || 'No evaluation available'}
                          </div>
                        </div>
                        
                        <div>
                          <p className="text-xs font-medium text-purple-700 mb-1">Next goal:</p>
                          <div className="text-sm text-purple-800 bg-white/70 border border-purple-200 rounded p-2">
                            {step.brainState.actions[0]?.nextGoal || 'No next goal available'}
                          </div>
                        </div>
                        
                        <div>
                          <p className="text-xs font-medium text-purple-700 mb-1">Memory:</p>
                          <div className="text-sm text-purple-800 bg-white/70 border border-purple-200 rounded p-2">
                            {step.brainState.actions[0]?.memory || 'No memory available'}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Actions Section (Light Blue) */}
                    <div className="space-y-3 mb-4">
                      <div className="text-sm font-medium text-gray-700 mb-2">Actions taken:</div>
                      {step.brainState.actions.map((action, index) => (
                        <div key={action.id} className="bg-indigo-50 border border-indigo-200 rounded-lg overflow-hidden">
                          <div className="flex items-center justify-between p-3 bg-indigo-100/50">
                            <div className="flex items-center space-x-2">
                              {getActionIcon(action.actionType, action.icon)}
                              <span className="text-sm font-medium text-indigo-800">
                                {action.actionType}
                              </span>
                            </div>
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${
                              action.status === 'passed' 
                                ? 'text-green-600 bg-green-50 border-green-200' 
                                : 'text-red-600 bg-red-50 border-red-200'
                            }`}>
                              {action.status.toUpperCase()}
                            </span>
                          </div>
                          
                          <div className="p-3">
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                              <div className="lg:col-span-2">
                                <div className="space-y-2 text-sm">
                                  {action.url && (
                                    <div className="flex items-center space-x-2">
                                      <span className="text-xs font-medium text-indigo-700 min-w-16">URL:</span>
                                      <span className="text-xs text-indigo-800 bg-white/70 px-2 py-1 rounded break-all font-mono">
                                        {action.url}
                                      </span>
                                    </div>
                                  )}
                                  
                                  {action.xpath && action.xpath !== 'N/A' && (
                                    <div className="flex items-center space-x-2">
                                      <span className="text-xs font-medium text-indigo-700 min-w-16">XPath:</span>
                                      <span className="text-xs text-indigo-600 bg-indigo-100 px-2 py-1 rounded font-mono break-all">
                                        {action.xpath}
                                      </span>
                                    </div>
                                  )}
                                  
                                  {action.inputText && (
                                    <div className="flex items-center space-x-2">
                                      <span className="text-xs font-medium text-indigo-700 min-w-16">Input:</span>
                                      <span className="text-xs text-indigo-800 bg-white/70 px-2 py-1 rounded flex items-center space-x-1">
                                        {action.isSecret && <Lock className="w-3 h-3" />}
                                        <span>{action.inputText}</span>
                                      </span>
                                    </div>
                                  )}
                                  

                                </div>
                              </div>
                              
                              <div className="flex justify-center lg:justify-end">
                                {action.screenshot && action.screenshot !== 'No screenshot' ? (
                                  <div 
                                    className="w-48 h-32 bg-gray-100 border-2 border-gray-300 rounded-lg overflow-hidden cursor-pointer group hover:border-indigo-400 transition-all duration-200 relative"
                                    onClick={() => handleScreenshotClick(action.screenshot!, action)}
                                  >
                                    <img
                                      src={`${BASE_DOMAIN}/${action.screenshot}`}
                                      alt="Action screenshot"
                                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                                    />
                                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-200 flex items-center justify-center">
                                      <ZoomIn className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                                    </div>
                                  </div>
                                ) : (
                                  <div className="w-48 h-32 bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
                                    <div className="text-center">
                                      <Image className="h-6 w-6 text-gray-400 mx-auto mb-1" />
                                      <p className="text-xs text-gray-500">No screenshot</p>
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}

                {/* Regular Step Content (Expected/Actual for non-brain state steps) */}
                {!step.brainState && (
                  <>
                    {step.expected && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-2">Expected:</p>
                        <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                          <p className="text-sm text-blue-800">{step.expected}</p>
                        </div>
                      </div>
                    )}
                    
                    {step.actual && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-2">Actual:</p>
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
                    )}
                    
                    {step.screenshot && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-2">Screenshot:</p>
                        <div 
                          className="bg-gray-100 border border-gray-200 rounded-lg overflow-hidden cursor-pointer group hover:border-indigo-400 transition-all duration-200 relative h-48 w-full max-w-md"
                          onClick={() => handleScreenshotClick(step.screenshot!, { 
                            actionType: step.description,
                            status: step.status as 'passed' | 'failed'
                          })}
                        >
                          <img
                            src={`${BASE_DOMAIN}/${step.screenshot}`}
                            alt="Step screenshot"
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                          />
                          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-200 flex items-center justify-center">
                            <ZoomIn className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}
                
                {/* Error Details */}
                {step.error && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Error details:</p>
                    <div className="bg-red-50 border border-red-200 rounded-md p-3">
                      <p className="text-sm text-red-800">{step.error}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        
        {testRun.steps.length === 0 && (
          <div className="text-center py-8">
            <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-800 mb-2">No execution steps</h3>
            <p className="text-gray-600">This test run hasn't been executed yet or has no recorded steps.</p>
          </div>
        )}
      </div>

      {/* Global Error */}
      {testRun.error && (
        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Test run error</h3>
              <p className="text-sm text-red-700 mt-1">{testRun.error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Screenshot Modal */}
      {selectedActionData && (
        <ScreenshotModal
          isOpen={modalOpen}
          onClose={closeModal}
          screenshot={selectedScreenshot}
          actionData={selectedActionData}
        />
      )}
    </div>
  );
}; 