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

    // Transform extra_rules string into ExtraRule array
    const extraRules = backendTestCase.extra_rules 
      ? backendTestCase.extra_rules.split('\n').filter(rule => rule.trim()).map((rule, index) => ({
          id: `rule-${backendTestCase.id}-${index + 1}`,
          ruleNumber: index + 1,
          description: rule.trim()
        }))
      : [];

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

    // Create empty secrets array (backend doesn't seem to have secrets in test case response)
    const secrets: TestSecret[] = [];

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
      passRate: 0, // Would need to be calculated from test runs
      totalRuns: 0, // Would need to be calculated from test runs
      passedRuns: 0, // Would need to be calculated from test runs
      failedRuns: 0, // Would need to be calculated from test runs
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
    extra_rules: string;
    url_route: string;
    allowed_domains: string[];
    priority: TestPriority;
    category?: string;
  }): Promise<FrontendTestCase> {
    try {
      const response = await apiClient.post<BackendTestCase>(this.ENDPOINTS.TEST_CASES, testCase);
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
    extra_rules: string;
    url_route: string;
    allowed_domains: string[];
    priority: TestPriority;
    category: string;
  }>): Promise<FrontendTestCase> {
    try {
      const response = await apiClient.put<BackendTestCase>(`${this.ENDPOINTS.TEST_CASES}${id}`, testCase);
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
}

export default TestCaseService; 