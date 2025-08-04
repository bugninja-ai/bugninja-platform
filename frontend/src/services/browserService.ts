import { apiClient } from './api';
import { ApiError } from '../types';

export interface BrowserType {
  value: string;
  label: string;
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

export class BrowserService {
  private static readonly ENDPOINTS = {
    BROWSER_TYPES: '/browser-types',
    SECRET_VALUES: '/secret-values/project',
    BROWSER_CONFIGS: '/browser-configs/project',
  };

  /**
   * Fetch available browser types
   */
  static async getBrowserTypes(): Promise<BrowserType[]> {
    try {
      const response = await apiClient.get<string[]>(this.ENDPOINTS.BROWSER_TYPES);
      
      // Transform array of strings to options format
      return response.data.map(type => ({
        value: type,
        label: type
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
}

export default BrowserService;