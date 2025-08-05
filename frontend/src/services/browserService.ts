import { apiClient } from './api';
import { ApiError } from '../types';

export interface BrowserType {
  value: string;
  label: string;
}

export interface BrowserConfigOptions {
  browser_channels: string[];
  user_agents: string[];
  viewport_sizes: Array<{ width: number; height: number }>;
}

export interface SecretValue {
  id: string;
  project_id: string;
  created_at: string;
  updated_at: string;
  secret_name: string;
  secret_value: string;
}

export interface BrowserConfigData {
  id: string;
  project_id: string;
  created_at: string;
  updated_at: string;
  browser_config: {
    browser_channel?: string;
    user_agent?: string;
    viewport?: {
      width: number;
      height: number;
    };
    device_scale_factor?: number;
    color_scheme?: string;
    accept_downloads?: boolean;
    proxy?: boolean;
    client_certificates?: any[];
    extra_http_headers?: Record<string, string>;
    http_credentials?: any;
    java_script_enabled?: boolean;
    geolocation?: any;
    timeout?: number;
    headers?: Record<string, string>;
    allowed_domains?: string[];
  };
}

export interface UpdateBrowserConfigWithId {
  id: string;
  browser_config: {
    browser_channel?: string;
    user_agent?: string;
    viewport?: {
      width: number;
      height: number;
    };
    geolocation?: {
      latitude: number;
      longitude: number;
    };
  };
}

export interface CreateBrowserConfigRequest {
  test_case_id: string;
  browser_config: {
    browser_channel?: string;
    user_agent?: string;
    viewport?: {
      width: number;
      height: number;
    };
    geolocation?: {
      latitude: number;
      longitude: number;
    };
  };
}

export interface BulkUpdateBrowserConfigRequest {
  browser_configs: UpdateBrowserConfigWithId[];
  new_browser_configs: CreateBrowserConfigRequest[];
  existing_browser_config_ids_to_add: string[];
  browser_config_ids_to_unlink: string[];
  test_case_id?: string;
}

export interface BulkUpdateBrowserConfigResponse {
  updated_browser_configs: BrowserConfigData[];
  created_browser_configs: BrowserConfigData[];
  linked_browser_configs: BrowserConfigData[];
  total_updated: number;
  total_created: number;
  total_linked: number;
  total_unlinked: number;
  failed_updates: any[];
  failed_creations: any[];
  failed_links: any[];
}

export class BrowserService {
  private static readonly ENDPOINTS = {
    BROWSER_TYPES: '/browser-types',
    SECRET_VALUES: '/secret-values/project',
    BROWSER_CONFIGS: '/browser-configs/project',
    BROWSER_CONFIGS_BULK: '/browser-configs/bulk',
  };

  /**
   * Fetch all browser configuration options from backend constants
   */
  static async getBrowserConfigOptions(): Promise<BrowserConfigOptions> {
    try {
      const response = await apiClient.get<BrowserConfigOptions>(this.ENDPOINTS.BROWSER_TYPES);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to fetch browser configuration options',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Fetch available browser types (for backward compatibility)
   * @deprecated Use getBrowserConfigOptions() instead
   */
  static async getBrowserTypes(): Promise<BrowserType[]> {
    try {
      const options = await this.getBrowserConfigOptions();
      
      // Transform browser channels to options format for backward compatibility
      return options.browser_channels.map(channel => ({
        value: channel,
        label: channel
      }));
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to fetch browser types',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Fetch secret values for a project
   */
  static async getSecretsByProject(
    projectId: string,
    params?: {
      page?: number;
      page_size?: number;
    }
  ): Promise<SecretValue[]> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

      const url = `${this.ENDPOINTS.SECRET_VALUES}/${projectId}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
      
      const response = await apiClient.get<SecretValue[]>(url);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to fetch secrets',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Fetch browser configurations for a project
   */
  static async getBrowserConfigsByProject(
    projectId: string,
    params?: {
      page?: number;
      page_size?: number;
    }
  ): Promise<BrowserConfigData[]> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

      const url = `${this.ENDPOINTS.BROWSER_CONFIGS}/${projectId}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
      
      const response = await apiClient.get<BrowserConfigData[]>(url);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to fetch browser configurations',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }

  /**
   * Bulk update browser configurations
   */
  static async bulkUpdateBrowserConfigs(requestData: BulkUpdateBrowserConfigRequest): Promise<BulkUpdateBrowserConfigResponse> {
    try {
      const response = await apiClient.put<BulkUpdateBrowserConfigResponse>(
        this.ENDPOINTS.BROWSER_CONFIGS_BULK, 
        requestData
      );
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.detail || error.message || 'Failed to update browser configurations',
        status: error.response?.status,
        code: error.code,
      };
      throw apiError;
    }
  }
}

export default BrowserService;