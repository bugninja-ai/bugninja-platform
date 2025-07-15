import { TestCase, TestRun, TestStep, TestStatistics, TestStatus, TestPriority, TestCategory } from '../types';

// Mock Test Cases
export const mockTestCases: TestCase[] = [
  {
    id: '1',
    code: 'TC-001',
    title: 'User Login Authentication',
    description: 'Verify successful login with valid credentials for retail banking portal',
    priority: 'critical',
    category: 'authentication',
    status: 'passed',
    goal: 'Ensure secure authentication mechanism works correctly',
    createdAt: new Date('2023-12-01'),
    updatedAt: new Date('2024-01-15'),
    lastRunAt: new Date('2024-01-15'),
    passRate: 85,
    totalRuns: 20,
    passedRuns: 17,
    failedRuns: 3,
  },
  {
    id: '2',
    code: 'TC-002',
    title: 'Account Balance Inquiry',
    description: 'Test account balance retrieval for checking and savings accounts',
    priority: 'high',
    category: 'banking',
    status: 'failed',
    goal: 'Verify balance display accuracy and response time',
    createdAt: new Date('2023-12-02'),
    updatedAt: new Date('2024-01-14'),
    lastRunAt: new Date('2024-01-14'),
    passRate: 60,
    totalRuns: 15,
    passedRuns: 9,
    failedRuns: 6,
  },
  {
    id: '3',
    code: 'TC-003',
    title: 'Fund Transfer Process',
    description: 'Test money transfer between accounts with validation',
    priority: 'critical',
    category: 'banking',
    status: 'pending',
    goal: 'Ensure secure and accurate fund transfers',
    createdAt: new Date('2023-12-03'),
    updatedAt: new Date('2024-01-13'),
    passRate: 75,
    totalRuns: 12,
    passedRuns: 9,
    failedRuns: 3,
  },
  {
    id: '4',
    code: 'TC-004',
    title: 'Payment Processing',
    description: 'Test bill payment functionality with external payees',
    priority: 'high',
    category: 'payments',
    status: 'pending',
    goal: 'Validate payment processing and confirmation',
    createdAt: new Date('2023-12-04'),
    updatedAt: new Date('2024-01-12'),
    passRate: 90,
    totalRuns: 10,
    passedRuns: 9,
    failedRuns: 1,
  },
  {
    id: '5',
    code: 'TC-005',
    title: 'Security Logout',
    description: 'Test automatic session timeout and manual logout',
    priority: 'medium',
    category: 'security',
    status: 'skipped',
    goal: 'Ensure proper session management',
    createdAt: new Date('2023-12-05'),
    updatedAt: new Date('2024-01-11'),
    passRate: 95,
    totalRuns: 8,
    passedRuns: 8,
    failedRuns: 0,
  },
];

// Mock Test Steps
export const mockTestSteps: TestStep[] = [
  {
    id: 'step-1',
    stepNumber: 1,
    description: 'Navigate to account dashboard and verify user is logged in',
    expected: 'User dashboard displays with account balances visible',
    actual: 'Dashboard loaded successfully, showing checking ($2,500.00) and savings ($5,000.00) accounts',
    status: 'passed',
    duration: 0.8,
  },
  {
    id: 'step-2',
    stepNumber: 2,
    description: "Click on 'Transfer Funds' button in the main navigation",
    expected: 'Transfer funds page loads with form fields visible',
    actual: 'Transfer page loaded with source/destination dropdowns and amount field',
    status: 'passed',
    duration: 0.5,
  },
  {
    id: 'step-3',
    stepNumber: 3,
    description: 'Select source account (Checking) and destination account',
    expected: 'Both accounts are selectable in dropdown menus',
    actual: 'Successfully selected checking as source and savings as destination',
    status: 'passed',
    duration: 0.3,
  },
  {
    id: 'step-4',
    stepNumber: 4,
    description: 'Enter transfer amount of $100.00',
    expected: 'Amount field accepts numeric input with currency formatting',
    actual: 'Amount field accepted $100.00 with proper formatting',
    status: 'passed',
    duration: 0.2,
  },
  {
    id: 'step-5',
    stepNumber: 5,
    description: 'Click Submit button to initiate transfer',
    expected: 'Confirmation dialog appears with transfer details',
    actual: 'Error: Insufficient funds message displayed',
    status: 'failed',
    duration: 0.1,
    error: 'Expected confirmation dialog but received error message',
  },
  {
    id: 'step-6',
    stepNumber: 6,
    description: 'Verify transaction appears in transaction history',
    expected: 'New transaction listed in account history',
    actual: 'No transaction recorded due to previous failure',
    status: 'failed',
    duration: 0.0,
    error: 'Step skipped due to previous failure',
  },
];

// Mock Test Runs
export const mockTestRuns: TestRun[] = [
  {
    id: 'run-1',
    testCaseId: '1',
    testCase: mockTestCases[0],
    status: 'passed',
    startedAt: new Date('2024-01-15T10:30:00Z'),
    completedAt: new Date('2024-01-15T10:32:30Z'),
    duration: 2.3,
    steps: mockTestSteps.slice(0, 4),
    passedSteps: 4,
    failedSteps: 0,
    totalSteps: 4,
    environment: 'staging',
    browser: 'Chrome 120.0',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  },
  {
    id: 'run-2',
    testCaseId: '2',
    testCase: mockTestCases[1],
    status: 'failed',
    startedAt: new Date('2024-01-14T14:15:00Z'),
    completedAt: new Date('2024-01-14T14:17:45Z'),
    duration: 2.75,
    steps: mockTestSteps,
    passedSteps: 4,
    failedSteps: 2,
    totalSteps: 6,
    environment: 'staging',
    browser: 'Firefox 121.0',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0)',
  },
  {
    id: 'run-3',
    testCaseId: '1',
    testCase: mockTestCases[0],
    status: 'passed',
    startedAt: new Date('2024-01-13T09:45:00Z'),
    completedAt: new Date('2024-01-13T09:47:15Z'),
    duration: 2.25,
    steps: mockTestSteps.slice(0, 4),
    passedSteps: 4,
    failedSteps: 0,
    totalSteps: 4,
    environment: 'production',
    browser: 'Safari 17.1',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
  },
  {
    id: 'run-4',
    testCaseId: '3',
    testCase: mockTestCases[2],
    status: 'pending',
    startedAt: new Date('2024-01-12T16:20:00Z'),
    duration: 0,
    steps: [],
    passedSteps: 0,
    failedSteps: 0,
    totalSteps: 0,
    environment: 'staging',
    browser: 'Chrome 120.0',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  },
];

// Mock Statistics
export const mockStatistics: TestStatistics = {
  totalTests: 10,
  passedTests: 5,
  failedTests: 2,
  pendingTests: 2,
  skippedTests: 1,
  passRate: 50,
};

// Mock API functions
export const mockApi = {
  getTestCases: async (): Promise<TestCase[]> => {
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API delay
    return mockTestCases;
  },

  getTestCase: async (id: string): Promise<TestCase | null> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockTestCases.find(tc => tc.id === id) || null;
  },

  getTestRuns: async (testCaseId?: string): Promise<TestRun[]> => {
    await new Promise(resolve => setTimeout(resolve, 400));
    return testCaseId 
      ? mockTestRuns.filter(run => run.testCaseId === testCaseId)
      : mockTestRuns;
  },

  getTestRun: async (id: string): Promise<TestRun | null> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockTestRuns.find(run => run.id === id) || null;
  },

  getStatistics: async (): Promise<TestStatistics> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    return mockStatistics;
  },

  createTestCase: async (data: any): Promise<TestCase> => {
    await new Promise(resolve => setTimeout(resolve, 800));
    const newTestCase: TestCase = {
      id: Math.random().toString(36).substr(2, 9),
      code: `TC-${String(mockTestCases.length + 1).padStart(3, '0')}`,
      title: data.title,
      description: data.description,
      priority: data.priority,
      category: data.category,
      status: 'pending',
      goal: data.goal,
      createdAt: new Date(),
      updatedAt: new Date(),
      passRate: 0,
      totalRuns: 0,
      passedRuns: 0,
      failedRuns: 0,
    };
    mockTestCases.push(newTestCase);
    return newTestCase;
  },

  runTest: async (testCaseId: string): Promise<TestRun> => {
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate test execution
    const testCase = mockTestCases.find(tc => tc.id === testCaseId);
    if (!testCase) throw new Error('Test case not found');
    
    const newRun: TestRun = {
      id: Math.random().toString(36).substr(2, 9),
      testCaseId,
      testCase,
      status: Math.random() > 0.3 ? 'passed' : 'failed',
      startedAt: new Date(),
      completedAt: new Date(),
      duration: Math.random() * 5 + 1,
      steps: mockTestSteps.slice(0, Math.floor(Math.random() * 6) + 1),
      passedSteps: 0,
      failedSteps: 0,
      totalSteps: 0,
      environment: 'staging',
      browser: 'Chrome 120.0',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    };
    
    newRun.totalSteps = newRun.steps.length;
    newRun.passedSteps = newRun.steps.filter(s => s.status === 'passed').length;
    newRun.failedSteps = newRun.steps.filter(s => s.status === 'failed').length;
    
    mockTestRuns.unshift(newRun);
    return newRun;
  },
}; 