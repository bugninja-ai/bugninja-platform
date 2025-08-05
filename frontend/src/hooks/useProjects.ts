import { useState, useEffect } from 'react';
import { Project, ApiState, ApiError } from '../types';
import { ProjectService } from '../services/projectService';

export interface UseProjectsResult extends ApiState<Project[]> {
  refetch: () => Promise<void>;
  selectedProject: Project | null;
  setSelectedProject: (project: Project | null) => void;
  createProject: (projectData: { name: string; default_start_url: string }) => Promise<Project>;
}

export const useProjects = (): UseProjectsResult => {
  const [state, setState] = useState<ApiState<Project[]>>({
    data: null,
    loading: true,
    error: null,
  });
  
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const fetchProjects = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      // Fetch all projects (using a large page size to get all projects)
      const response = await ProjectService.getProjects({ page: 1, size: 100 });
      
      setState(prev => ({ 
        ...prev, 
        data: response.items, 
        loading: false, 
        error: null 
      }));
      
    } catch (error) {
      const apiError = error as ApiError;
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: apiError.message 
      }));
      console.error('Failed to fetch projects:', apiError);
    }
  };

  const refetch = async () => {
    await fetchProjects();
  };

  const createProject = async (projectData: { name: string; default_start_url: string }): Promise<Project> => {
    try {
      const newProject = await ProjectService.createProject(projectData);
      
      // Refetch projects to get the updated list
      await fetchProjects();
      
      // Auto-select the newly created project
      setSelectedProject(newProject);
      
      return newProject;
    } catch (error) {
      const apiError = error as ApiError;
      console.error('Failed to create project:', apiError);
      throw apiError;
    }
  };

  // Initial fetch on mount
  useEffect(() => {
    fetchProjects();
  }, []);

  // Save selected project to localStorage for persistence
  useEffect(() => {
    console.log('useProjects: selectedProject changed to:', selectedProject?.name, selectedProject?.id);
    if (selectedProject) {
      localStorage.setItem('selectedProjectId', selectedProject.id);
    }
  }, [selectedProject]);

  // Restore selected project from localStorage on mount
  useEffect(() => {
    if (!state.data || state.data.length === 0) return;
    
    const savedProjectId = localStorage.getItem('selectedProjectId');
    
    if (savedProjectId) {
      const savedProject = state.data.find(p => p.id === savedProjectId);
      if (savedProject) {
        setSelectedProject(savedProject);
        return;
      } else {
        // Clear invalid project ID from localStorage
        localStorage.removeItem('selectedProjectId');
      }
    }
    
    // If no saved project or invalid saved project, select first available
    if (!selectedProject && state.data.length > 0) {
      setSelectedProject(state.data[0]);
    }
  }, [state.data, selectedProject]);

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
    refetch,
    selectedProject,
    setSelectedProject,
    createProject,
  };
};