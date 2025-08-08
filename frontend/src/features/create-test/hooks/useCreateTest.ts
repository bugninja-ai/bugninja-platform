import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjects } from '../../../shared/hooks/useProjects';
import { BrowserService } from '../../settings/services/browserService';
import { SecretValue, BrowserConfigData, BrowserConfigOptions } from '../../settings/types';
import { TestCaseService } from '../../test-cases/services/testCaseService';
import { useDropdowns } from '../../../shared/hooks/useDropdowns';
import { useAsyncOperation } from '../../../shared/hooks/useAsyncOperation';

export interface CreateTestFormData {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  goal: string;
  startingUrl: string;
  allowedDomains: string[];
  extraRules: { id: string; ruleNumber: number; description: string; }[];
  newBrowserConfigs: {
    id: string;
    browserChannel: string;
    userAgent: string;
    viewportSize: { width: number; height: number };
    geolocation?: { latitude: number; longitude: number };
  }[];
  existingBrowserConfigIds: string[];
  newSecrets: { id: string; secretName: string; value: string; }[];
  existingSecretIds: string[];
}

export interface UseCreateTestResult {
  // Form state
  method: 'upload' | 'manual';
  setMethod: (method: 'upload' | 'manual') => void;
  formData: CreateTestFormData;
  setFormData: React.Dispatch<React.SetStateAction<CreateTestFormData>>;
  file: File | null;
  setFile: (file: File | null) => void;
  
  // API data
  browserConfigOptions: BrowserConfigOptions | null;
  existingBrowserConfigs: BrowserConfigData[];
  existingSecrets: SecretValue[];
  loadingData: boolean;
  
  // Dropdown states
  dropdowns: {
    isOpen: (key: string) => boolean;
    toggle: (key: string) => void;
    open: (key: string) => void;
    close: (key: string) => void;
    closeAll: () => void;
  };
  
  // Form handlers
  handleInputChange: (field: string, value: string) => void;
  handleRuleChange: (index: number, value: string) => void;
  addRule: () => void;
  removeRule: (index: number) => void;
  handleDomainChange: (index: number, value: string) => void;
  addDomain: () => void;
  removeDomain: (index: number) => void;
  handleNewBrowserConfigChange: (index: number, field: string, value: any) => void;
  addNewBrowserConfig: () => void;
  removeNewBrowserConfig: (index: number) => void;
  removeExistingBrowserConfig: (configId: string) => void;
  addExistingBrowserConfig: (configId: string) => void;
  handleNewSecretChange: (index: number, field: string, value: string) => void;
  addNewSecret: () => void;
  removeNewSecret: (index: number) => void;
  removeExistingSecret: (secretId: string) => void;
  addExistingSecret: (secretId: string) => void;
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  
  // Submit
  loading: boolean;
  success: boolean;
  error: string | null;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
  
  // Options
  priorityOptions: { value: string; label: string; }[];
  categoryOptions: { value: string; label: string; }[];
}

export const useCreateTest = (): UseCreateTestResult => {
  const navigate = useNavigate();
  const { selectedProject } = useProjects();
  
  // Form state
  const [method, setMethod] = useState<'upload' | 'manual'>('manual');
  const [file, setFile] = useState<File | null>(null);
  
  // API Data states
  const [browserConfigOptions, setBrowserConfigOptions] = useState<BrowserConfigOptions | null>(null);
  const [existingBrowserConfigs, setExistingBrowserConfigs] = useState<BrowserConfigData[]>([]);
  const [existingSecrets, setExistingSecrets] = useState<SecretValue[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  
  // Dropdown management
  const dropdowns = useDropdowns();
  
  // Async operation management
  const { loading, success, error, execute: executeAsync, setSuccess } = useAsyncOperation();

  // Form data
  const [formData, setFormData] = useState<CreateTestFormData>({
    title: '',
    description: '',
    priority: 'medium',
    category: 'authentication',
    goal: '',
    startingUrl: '',
    allowedDomains: [''],
    extraRules: [{ id: '1', ruleNumber: 1, description: '' }],
    newBrowserConfigs: [{
      id: '1',
      browserChannel: '',
      userAgent: '',
      viewportSize: { width: 1920, height: 1080 },
      geolocation: undefined
    }],
    existingBrowserConfigIds: [],
    newSecrets: [],
    existingSecretIds: []
  });

  // Load data on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoadingData(true);
        
        if (!selectedProject?.id) {
          setLoadingData(false);
          return;
        }
        
        // Fetch browser configuration options from backend constants
        try {
          const configOptions = await BrowserService.getBrowserConfigOptions();
          setBrowserConfigOptions(configOptions);
        } catch (error) {
          console.error('Failed to load browser configuration options:', error);
          setBrowserConfigOptions(null);
        }

        try {
          const browserConfigsData = await BrowserService.getBrowserConfigsByProject(selectedProject.id);
          setExistingBrowserConfigs(browserConfigsData);
        } catch (error) {
          console.error('Failed to load browser configs:', error);
          setExistingBrowserConfigs([]);
        }

        try {
          const secretsData = await BrowserService.getSecretsByProject(selectedProject.id);
          setExistingSecrets(secretsData);
        } catch (error) {
          console.error('Failed to load secrets:', error);
          setExistingSecrets([]);
        }
        
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoadingData(false);
      }
    };

    loadData();
  }, [selectedProject?.id]);

  // Form handlers
  const handleInputChange = useCallback((field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // Extra Rules handlers
  const handleRuleChange = useCallback((index: number, value: string) => {
    const newRules = [...formData.extraRules];
    newRules[index] = { ...newRules[index], description: value };
    setFormData(prev => ({
      ...prev,
      extraRules: newRules
    }));
  }, [formData.extraRules]);

  const addRule = useCallback(() => {
    const newRule = {
      id: `rule-${Date.now()}`,
      ruleNumber: formData.extraRules.length + 1,
      description: ''
    };
    setFormData(prev => ({
      ...prev,
      extraRules: [...prev.extraRules, newRule]
    }));
  }, [formData.extraRules.length]);

  const removeRule = useCallback((index: number) => {
    if (formData.extraRules.length > 1) {
      const newRules = formData.extraRules.filter((_, i) => i !== index);
      // Renumber remaining rules
      const renumberedRules = newRules.map((rule, i) => ({ ...rule, ruleNumber: i + 1 }));
      setFormData(prev => ({
        ...prev,
        extraRules: renumberedRules
      }));
    }
  }, [formData.extraRules]);

  // Allowed Domains handlers
  const handleDomainChange = useCallback((index: number, value: string) => {
    const newDomains = [...formData.allowedDomains];
    newDomains[index] = value;
    setFormData(prev => ({
      ...prev,
      allowedDomains: newDomains
    }));
  }, [formData.allowedDomains]);

  const addDomain = useCallback(() => {
    setFormData(prev => ({
      ...prev,
      allowedDomains: [...prev.allowedDomains, '']
    }));
  }, []);

  const removeDomain = useCallback((index: number) => {
    if (formData.allowedDomains.length > 1) {
      const newDomains = formData.allowedDomains.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        allowedDomains: newDomains
      }));
    }
  }, [formData.allowedDomains]);

  // Browser Config handlers
  const handleNewBrowserConfigChange = useCallback((index: number, field: string, value: any) => {
    const newConfigs = [...formData.newBrowserConfigs];
    if (field === 'viewportSize.width' || field === 'viewportSize.height') {
      const [, dimension] = field.split('.');
      newConfigs[index] = {
        ...newConfigs[index],
        viewportSize: { ...newConfigs[index].viewportSize, [dimension]: value }
      };
    } else if (field.startsWith('geolocation.')) {
      const [, coord] = field.split('.');
      const currentGeo = newConfigs[index].geolocation || { latitude: 0, longitude: 0 };
      newConfigs[index] = {
        ...newConfigs[index],
        geolocation: { ...currentGeo, [coord]: value }
      };
    } else {
      newConfigs[index] = { ...newConfigs[index], [field]: value };
    }
    setFormData(prev => ({
      ...prev,
      newBrowserConfigs: newConfigs
    }));
  }, [formData.newBrowserConfigs]);

  const addNewBrowserConfig = useCallback(() => {
    const newConfig = {
      id: `config-${Date.now()}`,
      browserChannel: '',
      userAgent: '',
      viewportSize: { width: 1920, height: 1080 },
      geolocation: undefined
    };
    setFormData(prev => ({
      ...prev,
      newBrowserConfigs: [...prev.newBrowserConfigs, newConfig]
    }));
  }, []);

  const removeNewBrowserConfig = useCallback((index: number) => {
    const newConfigs = formData.newBrowserConfigs.filter((_, i) => i !== index);
    setFormData(prev => ({
      ...prev,
      newBrowserConfigs: newConfigs
    }));
  }, [formData.newBrowserConfigs]);

  const removeExistingBrowserConfig = useCallback((configId: string) => {
    setFormData(prev => ({
      ...prev,
      existingBrowserConfigIds: prev.existingBrowserConfigIds.filter(id => id !== configId)
    }));
  }, []);

  const addExistingBrowserConfig = useCallback((configId: string) => {
    setFormData(prev => ({
      ...prev,
      existingBrowserConfigIds: [...prev.existingBrowserConfigIds, configId]
    }));
  }, []);

  // Secrets handlers
  const handleNewSecretChange = useCallback((index: number, field: string, value: string) => {
    const newSecrets = [...formData.newSecrets];
    newSecrets[index] = { ...newSecrets[index], [field]: value };
    setFormData(prev => ({
      ...prev,
      newSecrets: newSecrets
    }));
  }, [formData.newSecrets]);

  const addNewSecret = useCallback(() => {
    const newSecret = {
      id: `secret-${Date.now()}`,
      secretName: '',
      value: ''
    };
    setFormData(prev => ({
      ...prev,
      newSecrets: [...prev.newSecrets, newSecret]
    }));
  }, []);

  const removeNewSecret = useCallback((index: number) => {
    const newSecrets = formData.newSecrets.filter((_, i) => i !== index);
    setFormData(prev => ({
      ...prev,
      newSecrets: newSecrets
    }));
  }, [formData.newSecrets]);

  const removeExistingSecret = useCallback((secretId: string) => {
    setFormData(prev => ({
      ...prev,
      existingSecretIds: prev.existingSecretIds.filter(id => id !== secretId)
    }));
  }, []);

  const addExistingSecret = useCallback((secretId: string) => {
    setFormData(prev => ({
      ...prev,
      existingSecretIds: [...prev.existingSecretIds, secretId]
    }));
  }, []);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await executeAsync(async () => {
        // Validation
        if (!selectedProject?.id) {
          throw new Error('Project must be selected!');
        }

        if (method === 'upload' && !file) {
          throw new Error('File must be uploaded!');
        }

        if (method === 'manual') {
          if (!formData.title.trim()) throw new Error('Test name is required!');
          if (!formData.description.trim()) throw new Error('Test description is required!');
          if (!formData.goal.trim()) throw new Error('Test goal is required!');
          if (!formData.startingUrl.trim()) throw new Error('Starting URL is required!');
          if (formData.allowedDomains.every(domain => !domain.trim())) {
            throw new Error('At least one domain must be specified!');
          }
        }

        // Build the payload
        const payload = {
          project_id: selectedProject?.id || '',
          document_id: file ? 'uploaded-document' : null,
          test_name: formData.title,
          test_description: formData.description,
          test_goal: formData.goal,
          extra_rules: formData.extraRules.map(rule => rule.description).filter(desc => desc.trim() !== ''),
          url_route: formData.startingUrl,
          allowed_domains: formData.allowedDomains.filter(domain => domain.trim() !== ''),
          priority: formData.priority as 'low' | 'medium' | 'high' | 'critical',
          category: formData.category,
          new_browser_configs: [], // Skip for now due to backend bug
          existing_browser_config_ids: formData.existingBrowserConfigIds,
          new_secret_values: [], // Skip for now due to backend bug  
          existing_secret_value_ids: formData.existingSecretIds
        };

        console.log('Creating test case with payload:', payload);
        
        const createdTestCase = await TestCaseService.createTestCase(payload);
        console.log('Test case created successfully:', createdTestCase);
        
        setTimeout(() => {
          navigate('/');
        }, 1500);
        
        return createdTestCase;
      });
    } catch (error) {
      console.error('Failed to create test case:', error);
      if (error instanceof Error) {
        alert(`Error: ${error.message}`);
      } else {
        alert('An unexpected error occurred!');
      }
    }
  }, [selectedProject?.id, method, file, formData, navigate, executeAsync]);

  const priorityOptions = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' },
  ];

  const categoryOptions = [
    { value: 'authentication', label: 'Authentication' },
    { value: 'banking', label: 'Banking' },
    { value: 'payments', label: 'Payments' },
    { value: 'security', label: 'Security' },
    { value: 'ui', label: 'UI' },
    { value: 'api', label: 'API' },
  ];

  return {
    // Form state
    method,
    setMethod,
    formData,
    setFormData,
    file,
    setFile,
    
    // API data
    browserConfigOptions,
    existingBrowserConfigs,
    existingSecrets,
    loadingData,
    
    // Dropdown states
    dropdowns,
    
    // Form handlers
    handleInputChange,
    handleRuleChange,
    addRule,
    removeRule,
    handleDomainChange,
    addDomain,
    removeDomain,
    handleNewBrowserConfigChange,
    addNewBrowserConfig,
    removeNewBrowserConfig,
    removeExistingBrowserConfig,
    addExistingBrowserConfig,
    handleNewSecretChange,
    addNewSecret,
    removeNewSecret,
    removeExistingSecret,
    addExistingSecret,
    handleFileChange,
    
    // Submit
    loading,
    success,
    error,
    handleSubmit,
    
    // Options
    priorityOptions,
    categoryOptions,
  };
};
