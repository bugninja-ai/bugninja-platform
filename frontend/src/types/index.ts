export type TestStatus = 'passed' | 'failed' | 'pending' | 'skipped';
export type TestPriority = 'critical' | 'high' | 'medium' | 'low';
export type TestCategory = 'authentication' | 'banking' | 'payments' | 'security' | 'ui' | 'api';

export interface BrainAction {
  id: string;
  actionType: string; // e.g., "Navigate to URL", "Fill text input", "Click login button"
  icon?: string;
  xpath?: string;
  url?: string; // The URL where this action was performed
  inputText?: string; // Text that was entered
  secretUsed?: string; // Name of secret that was used
  evaluatePreviousGoal: string;
  nextGoal: string;
  memory: string;
  status: 'passed' | 'failed';
  screenshot?: string;
}

export interface BrainState {
  id: string;
  stepNumber: number;
  description: string;
  actions: BrainAction[];
  status: TestStatus;
  duration: number;
}

export interface TestStep {
  id: string;
  stepNumber: number;
  description: string;
  expected?: string; // Optional for brain state steps
  actual?: string; // Optional for brain state steps
  status: TestStatus;
  duration: number; // in seconds
  screenshot?: string;
  error?: string;
  brainState?: BrainState; // This step is a brain state with multiple actions
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

// Project interfaces matching backend schema
export interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string; // ISO date string from backend
  updated_at: string; // ISO date string from backend
}

// API Response interfaces for pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export type ProjectsResponse = PaginatedResponse<Project>;

// API state interfaces
export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}

// Backend Test Case Types (matching API schema)
export interface BackendDocument {
  id: string;
  project_id: string;
  created_at: string;
  updated_at: string;
  name: string;
  content: string;
}

export interface BackendBrowserConfig {
  id: string;
  project_id: string;
  created_at: string;
  updated_at: string;
  browser_config: {
    user_agent: string;
    viewport: {
      width: number;
      height: number;
    };
    device_scale_factor: number;
    color_scheme: 'light' | 'dark';
    accept_downloads: boolean;
    client_certificates: any[];
    extra_http_headers: Record<string, string>;
    java_script_enabled: boolean;
    timeout: number;
    allowed_domains: string[];
    geolocation: {
      latitude: number;
      longitude: number;
    } | null;
  };
}

export interface BackendSecretValue {
  id: string;
  project_id: string;
  created_at: string;
  updated_at: string;
  secret_name: string;
  secret_value: string;
}

export interface BackendTestCase {
  id: string;
  project_id: string;
  document: BackendDocument | null;
  browser_configs: BackendBrowserConfig[];
  secrets: BackendSecretValue[];
  created_at: string;
  updated_at: string;
  test_name: string;
  test_description: string;
  test_goal: string;
  extra_rules: string[] | {
    id: string;
    rule_number: number;
    description: string;
  }[];
  url_routes: string;
  allowed_domains: string[];
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string | null;
  total_runs: number;
  passed_runs: number;
  failed_runs: number;
  success_rate: number;
}

export interface PaginatedTestCasesResponse {
  items: BackendTestCase[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// Transformed types for frontend usage
export interface FrontendTestCase {
  id: string;
  code: string;
  projectId: string;
  title: string;
  description: string;
  priority: TestPriority;
  category: TestCategory | 'general';
  status: TestStatus;
  goal: string;
  createdAt: Date;
  updatedAt: Date;
  lastRunAt?: Date;
  passRate: number;
  totalRuns: number;
  passedRuns: number;
  failedRuns: number;
  startingUrl: string;
  allowedDomains: string[];
  extraRules: ExtraRule[];
  browserConfigs: BrowserConfig[];
  secrets: TestSecret[];
  document: BackendDocument | null;
} 