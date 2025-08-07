import React from 'react';
import { Upload, X } from 'lucide-react';

interface FileUploadSectionProps {
  file: File | null;
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onFileRemove: () => void;
}

export const FileUploadSection: React.FC<FileUploadSectionProps> = ({
  file,
  onFileChange,
  onFileRemove
}) => {
  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 border border-gray-200 relative z-0">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Upload Test Case File</h2>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-indigo-400 transition-colors">
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Upload your test case file</h3>
        <p className="text-gray-600 mb-4">Drag and drop your file here, or click to select</p>
        
        <input
          type="file"
          accept=".csv,.json,.txt,.doc,.docx,.pdf,.xlsx,.xls,.rtf,.odt"
          onChange={onFileChange}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors cursor-pointer"
        >
          Select File
        </label>
        
        {file && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg flex items-center justify-between">
            <span className="text-sm text-gray-700">{file.name}</span>
            <button
              type="button"
              onClick={onFileRemove}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
