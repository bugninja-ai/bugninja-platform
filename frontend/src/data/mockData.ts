import { TestCase, TestRun, TestStep, TestStatistics, TestStatus, TestPriority, TestCategory, BrowserConfig, TestSecret, ExtraRule } from '../types';

// Mock Test Cases
export const mockTestCases: TestCase[] = [
  {
    id: '1',
    code: 'TC-001',
    projectId: 'prj-banking-001',
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
    startingUrl: 'https://banking.example.com/login',
    allowedDomains: ['banking.example.com', 'auth.example.com', 'api.example.com'],
    extraRules: [
      { id: 'rule-1', ruleNumber: 1, description: 'Verify HTTPS is enforced on all authentication pages' },
      { id: 'rule-2', ruleNumber: 2, description: 'Check for proper error handling on invalid credentials' },
      { id: 'rule-3', ruleNumber: 3, description: 'Ensure session timeout is configured correctly' }
    ],
    browserConfigs: [
      {
        id: 'config-1',
        name: 'Desktop Chrome',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1920, height: 1080 },
        geolocation: { latitude: 40.7128, longitude: -74.0060 }
      },
      {
        id: 'config-2',
        name: 'Mobile Safari',
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        viewport: { width: 375, height: 812 }
      }
    ],
    secrets: [
      { id: 'secret-1', secretName: 'TEST_USERNAME', value: 'test.user@example.com' },
      { id: 'secret-2', secretName: 'TEST_PASSWORD', value: 'SecurePass123!' },
      { id: 'secret-3', secretName: 'API_KEY', value: 'sk-1234567890abcdef' }
    ]
  },
  {
    id: '2',
    code: 'TC-002',
    projectId: 'prj-banking-001',
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
    startingUrl: 'https://banking.example.com/dashboard',
    allowedDomains: ['banking.example.com', 'api.example.com'],
    extraRules: [
      { id: 'rule-4', ruleNumber: 1, description: 'Verify balance updates in real-time' },
      { id: 'rule-5', ruleNumber: 2, description: 'Check for proper currency formatting' }
    ],
    browserConfigs: [
      {
        id: 'config-3',
        name: 'Firefox Desktop',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        viewport: { width: 1366, height: 768 }
      }
    ],
    secrets: [
      { id: 'secret-4', secretName: 'ACCOUNT_ID', value: 'ACC-1234567890' }
    ]
  },
  {
    id: '3',
    code: 'TC-003',
    projectId: 'prj-banking-001',
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
    startingUrl: 'https://banking.example.com/transfers',
    allowedDomains: ['banking.example.com', 'api.example.com', 'verification.example.com'],
    extraRules: [
      { id: 'rule-6', ruleNumber: 1, description: 'Validate transfer limits are enforced' },
      { id: 'rule-7', ruleNumber: 2, description: 'Check for proper transaction confirmation' },
      { id: 'rule-8', ruleNumber: 3, description: 'Verify audit trail is maintained' }
    ],
    browserConfigs: [
      {
        id: 'config-4',
        name: 'Edge Desktop',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        viewport: { width: 1440, height: 900 }
      }
    ],
    secrets: [
      { id: 'secret-5', secretName: 'SOURCE_ACCOUNT', value: 'CHK-9876543210' },
      { id: 'secret-6', secretName: 'DEST_ACCOUNT', value: 'SAV-1122334455' }
    ]
  },
  {
    id: '4',
    code: 'TC-004',
    projectId: 'prj-payments-002',
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
    startingUrl: 'https://payments.example.com/bills',
    allowedDomains: ['payments.example.com', 'external-payee.com'],
    extraRules: [
      { id: 'rule-9', ruleNumber: 1, description: 'Verify payment confirmation emails are sent' },
      { id: 'rule-10', ruleNumber: 2, description: 'Check for proper error handling on failed payments' }
    ],
    browserConfigs: [
      {
        id: 'config-5',
        name: 'Chrome Mobile',
        userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        viewport: { width: 393, height: 851 }
      }
    ],
    secrets: [
      { id: 'secret-7', secretName: 'PAYEE_ID', value: 'PAYEE-ELECTRIC-001' },
      { id: 'secret-8', secretName: 'PAYMENT_TOKEN', value: 'tok_1234567890' }
    ]
  },
  {
    id: '5',
    code: 'TC-005',
    projectId: 'prj-security-003',
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
    startingUrl: 'https://app.example.com/dashboard',
    allowedDomains: ['app.example.com', 'auth.example.com'],
    extraRules: [
      { id: 'rule-11', ruleNumber: 1, description: 'Verify session timeout after 30 minutes of inactivity' },
      { id: 'rule-12', ruleNumber: 2, description: 'Check for proper session cleanup on logout' }
    ],
    browserConfigs: [
      {
        id: 'config-6',
        name: 'Safari Desktop',
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        viewport: { width: 1680, height: 1050 }
      }
    ],
    secrets: [
      { id: 'secret-9', secretName: 'SESSION_TOKEN', value: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' }
    ]
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
      projectId: 'prj-default-001',
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
      startingUrl: 'https://app.example.com',
      allowedDomains: ['app.example.com'],
      extraRules: [],
      browserConfigs: [
        {
          id: 'config-default',
          name: 'Chrome Desktop',
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          viewport: { width: 1920, height: 1080 }
        }
      ],
      secrets: []
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