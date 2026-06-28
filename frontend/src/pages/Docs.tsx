import React from 'react';

export const Docs: React.FC = () => {
  return (
    <div className="h-full flex flex-col space-y-4">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-foreground tracking-tight">API Documentation</h1>
          <p className="text-sm text-muted mt-1">Interactive REST API documentation provided by Swagger UI.</p>
        </div>
      </div>
      <div className="flex-1 min-h-0 bg-white rounded-xl overflow-hidden border border-border shadow-xl">
        <iframe 
          src="http://127.0.0.1:8000/docs" 
          title="API Documentation"
          className="w-full h-full border-0"
        />
      </div>
    </div>
  );
};
