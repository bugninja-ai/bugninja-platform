import { apiClient } from './api';
import { 
  BackendTestCase, 
  PaginatedTestCasesResponse, 
  FrontendTestCase, 
  TestPriority,
  TestCategory,
  ApiError,
  ExtraRule,
  BrowserConfig,
  TestSecret
} from '../types';

export class TestCaseService {
  private static readonly ENDPOINTS = {
    TEST_CASES: '/test-cases/',
    TEST_RUNS: '/test-cases/{testCaseId}/test-runs',
    ALL_TEST_RUNS: '/test-runs/',
  };

  /**
   * Transform backend test case to frontend format
   */
  private static transformTestCase(backendTestCase: BackendTestCase): FrontendTestCase {
    // Generate a simple code from the test name (could be improved)
    const code = `TC-${backendTestCase.test_name.slice(0, 3).toUpperCase()}-${backendTestCase.id.slice(-4)}`;
    
    // Map backend priority to frontend priority
    const priorityMap: Record<string, TestPriority> = {
      'low': 'low',
      'medium': 'medium', 
      'high': 'high',
      'critical': 'critical'
    };

    // Map category or use 'general' as fallback
    const categoryMap: Record<string, TestCategory> = {
      'authentication': 'authentication',
      'banking': 'banking',
      'payments': 'payments',
      'security': 'security',
      'ui': 'ui',
      'api': 'api'
    };

    // Transform extra_rules array into ExtraRule array
    
    let extraRules: ExtraRule[] = [];
    
    if (backendTestCase.extra_rules) {
      if (Array.isArray(backendTestCase.extra_rules)) {
        // Check if array contains strings or objects
        const firstItem = backendTestCase.extra_rules[0];
        if (typeof firstItem === 'string') {
          // Handle array of strings
          extraRules = backendTestCase.extra_rules.map((rule, index) => ({
            id: `rule-${backendTestCase.id}-${index + 1}`,
            ruleNumber: index + 1,
            description: rule
          }));
        } else if (typeof firstItem === 'object' && firstItem !== null) {
          // Handle array of rule objects
          extraRules = backendTestCase.extra_rules.map((rule, index) => ({
            id: rule.id || `rule-${backendTestCase.id}-${index + 1}`,
            ruleNumber: rule.rule_number || index + 1,
            description: rule.description || ''
          }));
        }
      } else if (typeof backendTestCase.extra_rules === 'string') {
        // Handle legacy string format (split by newlines)
        extraRules = backendTestCase.extra_rules
          .split('\n')
          .filter(rule => rule.trim())
          .map((rule, index) => ({
            id: `rule-${backendTestCase.id}-${index + 1}`,
            ruleNumber: index + 1,
            description: rule.trim()
          }));
      }
    }

    // Transform backend browser configs to frontend format
    // Note: All data except 'name' comes directly from backend
    const browserConfigs: BrowserConfig[] = backendTestCase.browser_configs.map((backendConfig, index) => ({
      id: backendConfig.id, // ✅ Real backend data
      name: `Browser Config ${index + 1}`, // ⚠️ Generated (backend doesn't provide names)
      userAgent: backendConfig.browser_config.user_agent, // ✅ Real backend data
      viewport: {
        width: backendConfig.browser_config.viewport.width, // ✅ Real backend data
        height: backendConfig.browser_config.viewport.height, // ✅ Real backend data
      },
      geolocation: backendConfig.browser_config.geolocation ? {
        latitude: backendConfig.browser_config.geolocation.latitude,
        longitude: backendConfig.browser_config.geolocation.longitude
      } : undefined, // ✅ Real backend data (may be null)
    }));

    // Transform backend secrets to frontend format
    const secrets: TestSecret[] = backendTestCase.secrets?.map(secret => ({
      id: secret.id,
      secretName: secret.secret_name,
      value: secret.secret_value
    })) || [];

    return {
      id: backendTestCase.id,
      code,
      projectId: backendTestCase.project_id,
      title: backendTestCase.test_name,
      description: backendTestCase.test_description,
      priority: priorityMap[backendTestCase.priority] || 'medium',
      category: categoryMap[backendTestCase.category || ''] || 'general',
      status: 'pending', // Note: Test case status should come from latest test runs, not test case itself
      goal: backendTestCase.test_goal,
      createdAt: new Date(backendTestCase.created_at),
      updatedAt: new Date(backendTestCase.updated_at),
      lastRunAt: undefined, // Could be populated from test runs
      passRate: backendTestCase.success_rate,
      totalRuns: backendTestCase.total_runs,
      passedRuns: backendTestCase.passed_runs,
      failedRuns: backendTestCase.failed_runs,
      startingUrl: backendTestCase.url_routes,
      allowedDomains: backendTestCase.allowed_domains,
      extraRules,
      browserConfigs,
      secrets,
      document: backendTestCase.document
    };
  }

  /**
   * Fetch test cases with pagination and filtering
   */
  static async getTestCases(params?: {
    page?: number;
    page_size?: number;
    sort_order?: 'asc' | 'desc';
    project_id?: string;
    search?: string;
  }): Promise<{
    items: FrontendTestCase[];
    total_count: number;
    page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  }> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
      if (params?.sort_order) queryParams.append('sort_order', params.sort_order);
      if (params?.project_id) queryParams.append('project_id', params.project_id);

      const url = `${this.ENDPOINTS.TEST_CASES}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
      
      const response = await apiClient.get<PaginatedTestCasesResponse>(url);
      
      // Transform backend test cases to frontend format
      const transformedItems = response.data.items.map(this.transformTestCase);

      return {
        items: transformedItems,
        total_count: response.data.total_count,
        page: response.data.page,
        page_size: response.data.page_size,
        total_pages: response.data.total_pages,
        has_next: response.data.has_next,
        has_previous: response.data.has_previous
      };
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to fetch test cases',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Fetch a single test case by ID
   */
  static async getTestCase(id: string): Promise<FrontendTestCase> {
    try {
      const response = await apiClient.get<BackendTestCase>(`${this.ENDPOINTS.TEST_CASES}${id}`);
      return this.transformTestCase(response.data);
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to fetch test case',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Create a new test case
   */
  static async createTestCase(testCase: {
    project_id: string;
    document_id?: string;
    test_name: string;
    test_description: string;
    test_goal: string;
    extra_rules: ExtraRule[];
    url_route: string;
    allowed_domains: string[];
    priority: TestPriority;
    category?: string;
  }): Promise<FrontendTestCase> {
    try {
      const payload = {
        ...testCase,
        extra_rules: testCase.extra_rules.map(r => r.description).join('\n')
      };
      const response = await apiClient.post<BackendTestCase>(this.ENDPOINTS.TEST_CASES, payload);
      return this.transformTestCase(response.data);
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to create test case',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Update an existing test case
   */
  static async updateTestCase(id: string, testCase: Partial<{
    test_name: string;
    test_description: string;
    test_goal: string;
    extra_rules: ExtraRule[];
    url_route: string;
    allowed_domains: string[];
    priority: TestPriority;
    category: string;
  }>): Promise<FrontendTestCase> {
    try {
      const payload: Partial<{
        test_name: string;
        test_description: string;
        test_goal: string;
        extra_rules: string; // Changed to string for backend
        url_route: string;
        allowed_domains: string[];
        priority: TestPriority;
        category: string;
      }> = { ...testCase };

      if (testCase.extra_rules) {
        payload.extra_rules = testCase.extra_rules.map(r => r.description).join('\n');
      }

      const response = await apiClient.put<BackendTestCase>(`${this.ENDPOINTS.TEST_CASES}${id}`, payload);
      return this.transformTestCase(response.data);
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to update test case',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Delete a test case
   */
  static async deleteTestCase(id: string): Promise<void> {
    try {
      await apiClient.delete(`${this.ENDPOINTS.TEST_CASES}${id}`);
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to delete test case',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Fetch test runs for a specific test case
   */
  static async getTestRuns(testCaseId: string, params?: {
    page?: number;
    page_size?: number;
    sort_order?: 'asc' | 'desc';
  }): Promise<{
    items: any[];
    total_count: number;
    page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  }> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
      if (params?.sort_order) queryParams.append('sort_order', params.sort_order);

      const url = this.ENDPOINTS.TEST_RUNS.replace('{testCaseId}', testCaseId);
      const fullUrl = `${url}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
      
      const response = await apiClient.get<{
        items: any[];
        total_count: number;
        page: number;
        page_size: number;
        total_pages: number;
        has_next: boolean;
        has_previous: boolean;
      }>(fullUrl);
      
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to fetch test runs',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Fetch the most recent test runs for a test case (for display on detail page)
   */
  static async getRecentTestRuns(testCaseId: string, limit: number = 3): Promise<any[]> {
    try {
      const response = await this.getTestRuns(testCaseId, {
        page: 1,
        page_size: limit,
        sort_order: 'desc'
      });
      
      return response.items;
    } catch (error: any) {
      // If there's an error fetching test runs, return empty array rather than throwing
      console.warn('Failed to fetch recent test runs:', error.message);
      return [];
    }
  }

  /**
   * Fetch a single test run by ID
   */
  static async getTestRun(testRunId: string): Promise<any> {
    try {
      const response = await apiClient.get<any>(`/test-runs/${testRunId}`);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to fetch test run',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Fetch all test runs across all test cases with pagination
   */
  static async getAllTestRuns(params?: {
    page?: number;
    page_size?: number;
    sort_order?: 'asc' | 'desc';
    test_case_id?: string;
    search?: string;
    status?: string;
  }): Promise<{
    items: any[];
    total_count: number;
    page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  }> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
      if (params?.sort_order) queryParams.append('sort_order', params.sort_order);
      if (params?.test_case_id) queryParams.append('test_case_id', params.test_case_id);
      if (params?.search) queryParams.append('search', params.search);
      if (params?.status) queryParams.append('status', params.status);

      const url = `${this.ENDPOINTS.ALL_TEST_RUNS}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
      
      const response = await apiClient.get<{
        items: any[];
        total_count: number;
        page: number;
        page_size: number;
        total_pages: number;
        has_next: boolean;
        has_previous: boolean;
      }>(url);
      
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to fetch test runs',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }
}

export default TestCaseService; 