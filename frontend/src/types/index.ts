export type TestStatus = 'passed' | 'failed' | 'pending' | 'skipped';
export type TestPriority = 'critical' | 'high' | 'medium' | 'low';
export type TestCategory = 'authentication' | 'banking' | 'payments' | 'security' | 'ui' | 'api';

export interface TestStep {
  id: string;
  stepNumber: number;
  description: string;
  expected: string;
  actual: string;
  status: TestStatus;
  duration: number; // in seconds
  screenshot?: string;
  error?: string;
}

export interface BrowserConfig {
  id: string;
  name: string;
  userAgent: string;
  viewport: {
    width: number;
    height: number;
  };
  geolocation?: {
    latitude: number;
    longitude: number;
  };
}

export interface TestSecret {
  id: string;
  secretName: string;
  value: string;
}

export interface ExtraRule {
  id: string;
  ruleNumber: number;
  description: string;
}

export interface TestCase {
  id: string;
  code: string; // e.g., "TC-001"
  projectId: string;
  title: string;
  description: string;
  priority: TestPriority;
  category: TestCategory;
  status: TestStatus;
  goal: string;
  createdAt: Date;
  updatedAt: Date;
  lastRunAt?: Date;
  passRate: number; // percentage
  totalRuns: number;
  passedRuns: number;
  failedRuns: number;
  // Additional configuration fields
  startingUrl: string;
  allowedDomains: string[];
  extraRules: ExtraRule[];
  browserConfigs: BrowserConfig[];
  secrets: TestSecret[];
}

export interface TestRun {
  id: string;
  testCaseId: string;
  testCase: TestCase;
  status: TestStatus;
  startedAt: Date;
  completedAt?: Date;
  duration: number; // in seconds
  steps: TestStep[];
  passedSteps: number;
  failedSteps: number;
  totalSteps: number;
  environment: string;
  browser: string;
  userAgent: string;
  error?: string;
}

export interface TestStatistics {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  pendingTests: number;
  skippedTests: number;
  passRate: number;
}

export interface TestFilters {
  status?: TestStatus[];
  priority?: TestPriority[];
  category?: TestCategory[];
  search?: string;
  dateFrom?: Date;
  dateTo?: Date;
}

export interface CreateTestCaseRequest {
  title: string;
  description: string;
  priority: TestPriority;
  category: TestCategory;
  goal: string;
  steps?: string[];
  file?: File;
} 