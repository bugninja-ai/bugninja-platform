import { useState, useEffect, useCallback } from 'react';
import { ApiState, ApiError } from '../types';
import { TestCaseService } from '../services/testCaseService';

export interface UseTestRunsParams {
  page?: number;
  pageSize?: number;
  search?: string;
  status?: string;
  sortOrder?: 'asc' | 'desc';
  testTraversalId?: string;
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
  setTestTraversalId: (id: string | undefined) => void;
  
  // Current filters
  filters: {
    search: string;
    status?: string;
    sortOrder: 'asc' | 'desc';
    testTraversalId?: string;
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
  const [testTraversalId, setTestTraversalIdState] = useState<string | undefined>(initialParams?.testTraversalId);

  const fetchTestRuns = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await TestCaseService.getAllTestRuns({
        page,
        page_size: pageSize,
        sort_order: sortOrder,
        test_traversal_id: testTraversalId,
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
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: apiError.message 
      }));
      console.error('Failed to fetch test runs:', apiError);
    }
  }, [page, pageSize, sortOrder, testTraversalId]);

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

  const setTestTraversalId = useCallback((newId: string | undefined) => {
    setTestTraversalIdState(newId);
    setPageState(1); // Reset to first page when filtering
  }, []);

  // Fetch data when dependencies change
  useEffect(() => {
    fetchTestRuns();
  }, [fetchTestRuns]);

  // Client-side filtering for search and status since backend might not support all filters
  const filteredData = state.data?.filter(testRun => {
    if (search) {
      const searchLower = search.toLowerCase();
      const matchesSearch = 
        (testRun.test_case?.test_name?.toLowerCase().includes(searchLower)) ||
        (testRun.test_case?.test_description?.toLowerCase().includes(searchLower)) ||
        (testRun.id?.toLowerCase().includes(searchLower));
      if (!matchesSearch) return false;
    }
    
    if (status && status !== 'all' && testRun.status !== status) {
      return false;
    }
    
    return true;
  }) || null;

  return {
    data: filteredData,
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
    setTestTraversalId,
    filters: {
      search,
      status,
      sortOrder,
      testTraversalId,
    },
  };
}; 