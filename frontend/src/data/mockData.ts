import { TestCase, TestRun, TestStep, TestStatistics, TestStatus, TestPriority, TestCategory, BrowserConfig, TestSecret, ExtraRule, BrainAction, BrainState } from '../types';

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
    description: 'AI Brain State: Navigate to login and authenticate user',
    status: 'passed',
    duration: 2.3,
    brainState: {
      id: 'brain-state-1',
      stepNumber: 1,
      description: 'Navigate to login and authenticate user',
      status: 'passed',
      duration: 2.3,
      actions: [
        {
          id: 'action-1',
          actionType: 'Navigate to URL',
          icon: 'globe',
          xpath: 'N/A',
          url: 'https://app.bacprep.to',
          evaluatePreviousGoal: 'Unknown - This is the initial state. The browser is open on a blank page. No actions have been taken yet.',
          nextGoal: 'Navigate to https://app.bacprep.to to access the login page.',
          memory: 'Initial state. Need to go to app.bacprep.to to begin the login process. 0 out of 4 main steps completed: 1) Login, 2) Edit username, 3) Logout, 4) Close browser.',
          status: 'passed',
          screenshot: 'screenshot-1-action-1.png'
        },
        {
          id: 'action-2',
          actionType: 'Fill text input',
          icon: 'edit',
          xpath: '/html/body/div[1]/div/div/form/div[1]/input',
          url: 'https://app.bacprep.to/hu/login',
          secretUsed: 'TEST_USERNAME',
          inputText: 'test.user@example.com',
          evaluatePreviousGoal: 'Success - Navigated to the login page of app.bacprep.to. The login form is visible with fields for email and password, and a login button.',
          nextGoal: 'Fill in the email field with the provided credentials.',
          memory: 'Navigated to https://app.bacprep.to/hu/login. Ready to log in. 0 out of 4 main steps completed: 1) Login, 2) Edit username, 3) Logout, 4) Close browser.',
          status: 'passed',
          screenshot: 'screenshot-1-action-2.png'
        },
        {
          id: 'action-3',
          actionType: 'Fill password input',
          icon: 'lock',
          xpath: '/html/body/div[1]/div/div/form/div[2]/input',
          url: 'https://app.bacprep.to/hu/login',
          secretUsed: 'TEST_PASSWORD',
          inputText: '••••••••••••',
          evaluatePreviousGoal: 'Success - Email field filled successfully with test credentials.',
          nextGoal: 'Fill in the password field with the provided credentials.',
          memory: 'Email entered. Now need to enter password to complete login form. 0 out of 4 main steps completed: 1) Login, 2) Edit username, 3) Logout, 4) Close browser.',
          status: 'passed',
          screenshot: 'screenshot-1-action-3.png'
        },
        {
          id: 'action-4',
          actionType: 'Click login button',
          icon: 'mouse-pointer',
          xpath: '/html/body/div[1]/div/div/form/button',
          url: 'https://app.bacprep.to/hu/login',
          evaluatePreviousGoal: 'Success - Both email and password fields are filled with valid credentials.',
          nextGoal: 'Click the login button to submit credentials and authenticate.',
          memory: 'Login form completed with credentials. Ready to submit form. 0 out of 4 main steps completed: 1) Login, 2) Edit username, 3) Logout, 4) Close browser.',
          status: 'passed',
          screenshot: 'screenshot-1-action-4.png'
        }
      ]
    }
  },
  {
    id: 'step-2',
    stepNumber: 2,
    description: 'AI Brain State: Handle post-login popup and navigate to profile',
    status: 'passed',
    duration: 1.2,
    brainState: {
      id: 'brain-state-2',
      stepNumber: 2,
      description: 'Handle post-login popup and navigate to profile',
      status: 'passed',
      duration: 1.2,
      actions: [
        {
          id: 'action-5',
          actionType: 'Wait for page load',
          icon: 'clock',
          xpath: 'N/A',
          url: 'https://app.bacprep.to/dashboard',
          evaluatePreviousGoal: 'Success - Login was successful. The dashboard loaded and a popup about Instagram appeared. The user is authenticated and on the main page.',
          nextGoal: 'Wait for page to fully load and identify the popup element.',
          memory: 'Logged in successfully (1/4 main steps done). Instagram popup is blocking the dashboard. Need to close it before proceeding.',
          status: 'passed',
          screenshot: 'screenshot-2-action-1.png'
        },
        {
          id: 'action-6',
          actionType: 'Close popup dialog',
          icon: 'x',
          xpath: '/html/body/div[2]/div/div/div[3]/button',
          url: 'https://app.bacprep.to/dashboard',
          evaluatePreviousGoal: 'Success - Page loaded and popup is visible and blocking dashboard access.',
          nextGoal: 'Close the Instagram popup by clicking the "Bezárás" (close) button.',
          memory: 'Instagram popup identified. Need to close it to access dashboard functionality for username editing.',
          status: 'passed',
          screenshot: 'screenshot-2-action-2.png'
        }
      ]
    }
  },
  {
    id: 'step-3',
    stepNumber: 3,
    description: 'AI Brain State: Attempt to edit username',
    status: 'failed',
    duration: 1.8,
    brainState: {
      id: 'brain-state-3',
      stepNumber: 3,
      description: 'Attempt to edit username',
      status: 'failed',
      duration: 1.8,
      actions: [
        {
          id: 'action-7',
          actionType: 'Click user profile',
          icon: 'user',
          xpath: '/html/body/header/div/div[2]/div/button',
          url: 'https://app.bacprep.to/dashboard',
          evaluatePreviousGoal: 'Success - Successfully closed Instagram popup and can now see the dashboard clearly.',
          nextGoal: 'Navigate to profile section to edit username as requested.',
          memory: 'Dashboard is now accessible. Need to edit username next. 1 out of 4 main steps completed: 1) Login, 2) Edit username, 3) Logout, 4) Close browser.',
          status: 'passed',
          screenshot: 'screenshot-3-action-1.png'
        },
        {
          id: 'action-8',
          actionType: 'Wait for menu',
          icon: 'clock',
          xpath: 'N/A',
          url: 'https://app.bacprep.to/dashboard',
          evaluatePreviousGoal: 'Success - Clicked on user profile area, waiting for menu or profile page to load.',
          nextGoal: 'Wait for profile menu or settings page to appear.',
          memory: 'Clicked user profile button. Waiting for navigation or dropdown menu to appear with edit options.',
          status: 'passed',
          screenshot: 'screenshot-3-action-2.png'
        },
        {
          id: 'action-9',
          actionType: 'Search for settings',
          icon: 'search',
          xpath: 'N/A',
          url: 'https://app.bacprep.to/dashboard',
          evaluatePreviousGoal: 'Failed - Could not locate profile section or edit username functionality in the expected locations.',
          nextGoal: 'Search for alternative methods to access user settings or profile editing.',
          memory: 'Unable to find username edit option. May need to look in different menu or settings area. Profile dropdown may not have edit functionality.',
          status: 'failed',
          screenshot: 'screenshot-3-action-3.png'
        }
      ]
    }
  }
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
    steps: mockTestSteps.slice(0, 2),
    passedSteps: 2,
    failedSteps: 0,
    totalSteps: 2,
    environment: 'staging',
    browser: 'Chrome 120.0',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
    passedSteps: 2,
    failedSteps: 1,
    totalSteps: 3,
    environment: 'staging',
    browser: 'Firefox 121.0',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0)'
  },
  {
    id: 'run-3',
    testCaseId: '1',
    testCase: mockTestCases[0],
    status: 'passed',
    startedAt: new Date('2024-01-13T09:45:00Z'),
    completedAt: new Date('2024-01-13T09:47:15Z'),
    duration: 2.25,
    steps: mockTestSteps.slice(0, 2),
    passedSteps: 2,
    failedSteps: 0,
    totalSteps: 2,
    environment: 'production',
    browser: 'Safari 17.1',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
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
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
      steps: mockTestSteps.slice(0, Math.floor(Math.random() * 3) + 1),
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