
import React from 'react';

const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex flex-col items-center space-y-4 py-8 animate-fade-in">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-gray-200 border-t-primary rounded-full animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 bg-primary/20 rounded-full animate-pulse"></div>
        </div>
      </div>
      <div className="text-center">
        <p className="text-lg font-medium text-gray-700 mb-1">Analyzing your resume...</p>
        <p className="text-sm text-gray-500">This may take a few moments</p>
      </div>
      <div className="w-64 bg-gray-200 rounded-full h-2">
        <div className="bg-primary h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
