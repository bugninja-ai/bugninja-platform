import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  Target, 
  AlertTriangle, 
  CheckCircle,
  X,
  Plus,
  Trash2
} from 'lucide-react';
import { TestPriority, TestCategory, CreateTestCaseRequest } from '../types';
import { mockApi } from '../data/mockData';

export const CreateTest: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<CreateTestCaseRequest>({
    title: '',
    description: '',
    priority: 'medium',
    category: 'banking',
    goal: '',
    steps: ['']
  });
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [useManualInput, setUseManualInput] = useState(true);

  const handleInputChange = (field: keyof CreateTestCaseRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleStepChange = (index: number, value: string) => {
    const newSteps = [...(formData.steps || [])];
    newSteps[index] = value;
    setFormData(prev => ({
      ...prev,
      steps: newSteps
    }));
  };

  const addStep = () => {
    setFormData(prev => ({
      ...prev,
      steps: [...(prev.steps || []), '']
    }));
  };

  const removeStep = (index: number) => {
    const newSteps = (formData.steps || []).filter((_, i) => i !== index);
    setFormData(prev => ({
      ...prev,
      steps: newSteps
    }));
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      setUploadedFile(files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      setUploadedFile(files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title || !formData.description) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      const testCase = await mockApi.createTestCase({
        ...formData,
        file: uploadedFile || undefined
      });
      
      // Navigate to test cases page or show success message
      navigate('/test-cases');
    } catch (error) {
      console.error('Failed to create test case:', error);
      alert('Failed to create test case. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Generate New Test Case</h1>
          <p className="text-muted-foreground">Create automated test cases by uploading documents or providing manual input</p>
        </div>

        {/* Input Method Toggle */}
        <div className="bg-card border border-border rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-foreground mb-4">Input Method</h2>
          <div className="flex space-x-4">
            <button
              onClick={() => setUseManualInput(true)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md border transition-colors ${
                useManualInput 
                  ? 'bg-primary text-primary-foreground border-primary' 
                  : 'bg-background text-muted-foreground border-border hover:bg-accent'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>Manual Input</span>
            </button>
            <button
              onClick={() => setUseManualInput(false)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md border transition-colors ${
                !useManualInput 
                  ? 'bg-primary text-primary-foreground border-primary' 
                  : 'bg-background text-muted-foreground border-border hover:bg-accent'
              }`}
            >
              <Upload className="h-4 w-4" />
              <span>File Upload</span>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload Section */}
          {!useManualInput && (
            <div className="bg-card border border-border rounded-lg p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">Upload Test Documentation</h2>
              
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive 
                    ? 'border-primary bg-primary/5' 
                    : 'border-border hover:border-primary/50 hover:bg-accent/50'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {uploadedFile ? (
                  <div className="flex items-center justify-center space-x-2">
                    <FileText className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-medium text-foreground">{uploadedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setUploadedFile(null)}
                      className="p-1 text-muted-foreground hover:text-foreground"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ) : (
                  <>
                    <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-lg font-medium text-foreground mb-2">
                      Drop your test documentation here
                    </p>
                    <p className="text-muted-foreground mb-4">
                      or click to browse files
                    </p>
                    <input
                      type="file"
                      onChange={handleFileChange}
                      className="hidden"
                      id="file-upload"
                      accept=".pdf,.doc,.docx,.txt,.md"
                    />
                    <label
                      htmlFor="file-upload"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary bg-primary/10 hover:bg-primary/20 cursor-pointer transition-colors"
                    >
                      Choose File
                    </label>
                    <p className="text-xs text-muted-foreground mt-2">
                      Supports: PDF, DOC, DOCX, TXT, MD
                    </p>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Manual Input Section */}
          {useManualInput && (
            <div className="bg-card border border-border rounded-lg p-6">
              <h2 className="text-lg font-semibold text-foreground mb-6">Test Case Details</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Title */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Test Case Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                    placeholder="e.g., User Login Authentication Test"
                    required
                  />
                </div>

                {/* Priority */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Priority
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => handleInputChange('priority', e.target.value as TestPriority)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>

                {/* Category */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => handleInputChange('category', e.target.value as TestCategory)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="authentication">Authentication</option>
                    <option value="banking">Banking</option>
                    <option value="payments">Payments</option>
                    <option value="security">Security</option>
                    <option value="ui">UI</option>
                    <option value="api">API</option>
                  </select>
                </div>

                {/* Description */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Description *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                    placeholder="Describe what this test case validates..."
                    required
                  />
                </div>

                {/* Test Goal */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-foreground mb-2">
                    <Target className="h-4 w-4 inline mr-1" />
                    Test Goal *
                  </label>
                  <textarea
                    value={formData.goal}
                    onChange={(e) => handleInputChange('goal', e.target.value)}
                    rows={2}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                    placeholder="What should this test accomplish?"
                    required
                  />
                </div>

                {/* Test Steps */}
                <div className="md:col-span-2">
                  <div className="flex items-center justify-between mb-3">
                    <label className="block text-sm font-medium text-foreground">
                      Test Steps (Optional)
                    </label>
                    <button
                      type="button"
                      onClick={addStep}
                      className="flex items-center space-x-1 px-3 py-1 text-sm text-primary hover:bg-primary/10 rounded-md transition-colors"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Add Step</span>
                    </button>
                  </div>
                  
                  <div className="space-y-3">
                    {(formData.steps || []).map((step, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <span className="text-sm font-medium text-muted-foreground w-8">
                          {index + 1}.
                        </span>
                        <input
                          type="text"
                          value={step}
                          onChange={(e) => handleStepChange(index, e.target.value)}
                          className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                          placeholder={`Step ${index + 1} description...`}
                        />
                        {(formData.steps || []).length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeStep(index)}
                            className="p-1 text-muted-foreground hover:text-red-600 transition-colors"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* AI Processing Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-blue-800">AI Processing</h3>
                <p className="text-sm text-blue-700 mt-1">
                  Our AI will analyze your input and generate comprehensive test steps, including expected results and validation points. 
                  This process typically takes 30-60 seconds.
                </p>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => navigate('/test-cases')}
              className="px-4 py-2 border border-border rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              Cancel
            </button>
            
            <button
              type="submit"
              disabled={loading || (!formData.title || !formData.description || (!useManualInput && !uploadedFile))}
              className="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                  Generating Test Case...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Generate Test Case
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}; 