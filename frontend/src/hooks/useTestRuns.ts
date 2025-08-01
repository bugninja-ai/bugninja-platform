import { useState, useEffect, useCallback } from 'react';
import { ApiState, ApiError } from '../types';
import { TestCaseService } from '../services/testCaseService';

export interface UseTestRunsParams {
  page?: number;
  pageSize?: number;
  search?: string;
  status?: string;
  sortOrder?: 'asc' | 'desc';
  testCaseId?: string;
}

export interface UseTestRunsResult extends ApiState<any[]> {
  // Pagination info
  totalCount: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
  
  // Actions
  refetch: () => Promise<void>;
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  setSearch: (search: string) => void;
  setStatus: (status: string | undefined) => void;
  setSortOrder: (sortOrder: 'asc' | 'desc') => void;
  setTestCaseId: (id: string | undefined) => void;
  
  // Current filters
  filters: {
    search: string;
    status?: string;
    sortOrder: 'asc' | 'desc';
    testCaseId?: string;
  };
}

export const useTestRuns = (initialParams?: UseTestRunsParams): UseTestRunsResult => {
  const [state, setState] = useState<ApiState<any[]>>({
    data: null,
    loading: true,
    error: null,
  });

  // Pagination state
  const [page, setPageState] = useState(initialParams?.page || 1);
  const [pageSize, setPageSizeState] = useState(initialParams?.pageSize || 15);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);

  // Filter state
  const [search, setSearchState] = useState(initialParams?.search || '');
  const [status, setStatusState] = useState<string | undefined>(initialParams?.status);
  const [sortOrder, setSortOrderState] = useState<'asc' | 'desc'>(initialParams?.sortOrder || 'desc');
  const [testCaseId, setTestCaseIdState] = useState<string | undefined>(initialParams?.testCaseId);

  const fetchTestRuns = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await TestCaseService.getAllTestRuns({
        page,
        page_size: pageSize,
        sort_order: sortOrder,
        test_case_id: testCaseId,
        search: search || undefined,
        status: status || undefined,
      });
      
      setState(prev => ({ 
        ...prev, 
        data: response.items, 
        loading: false, 
        error: null 
      }));

      // Update pagination info
      setTotalCount(response.total_count);
      setTotalPages(response.total_pages);
      setHasNext(response.has_next);
      setHasPrevious(response.has_previous);
      
    } catch (error) {
      const apiError = error as ApiError;
      
      // If we get a 404 for test case not found, clear the filter and retry
      if (apiError.status === 404 && testCaseId && apiError.message?.includes('not found')) {
        console.warn('Test case not found, clearing filter and retrying...');
        setTestCaseIdState(undefined);
        return; // This will trigger a re-fetch with the cleared filter
      }
      
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: apiError.message 
      }));
      console.error('Failed to fetch test runs:', apiError);
    }
  }, [page, pageSize, sortOrder, testCaseId, search, status]);

  const refetch = useCallback(async () => {
    await fetchTestRuns();
  }, [fetchTestRuns]);

  // Reset to first page when filters change
  const setPage = useCallback((newPage: number) => {
    setPageState(newPage);
  }, []);

  const setPageSize = useCallback((newPageSize: number) => {
    setPageSizeState(newPageSize);
    setPageState(1); // Reset to first page when changing page size
  }, []);

  const setSearch = useCallback((newSearch: string) => {
    setSearchState(newSearch);
    setPageState(1); // Reset to first page when searching
  }, []);

  const setStatus = useCallback((newStatus: string | undefined) => {
    setStatusState(newStatus);
    setPageState(1); // Reset to first page when filtering
  }, []);

  const setSortOrder = useCallback((newSortOrder: 'asc' | 'desc') => {
    setSortOrderState(newSortOrder);
    setPageState(1); // Reset to first page when sorting
  }, []);

  const setTestCaseId = useCallback((newId: string | undefined) => {
    setTestCaseIdState(newId);
    setPageState(1); // Reset to first page when filtering
  }, []);

  // Fetch data when dependencies change
  useEffect(() => {
    fetchTestRuns();
  }, [fetchTestRuns]);

  // No client-side filtering needed - all filtering is handled by the backend

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
    totalCount,
    page,
    pageSize,
    totalPages,
    hasNext,
    hasPrevious,
    refetch,
    setPage,
    setPageSize,
    setSearch,
    setStatus,
    setSortOrder,
    setTestCaseId,
    filters: {
      search,
      status,
      sortOrder,
      testCaseId,
    },
  };
}; 