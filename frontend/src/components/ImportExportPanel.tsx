import React, { useState } from 'react';
import { emailService } from '../services/api';

interface ImportExportPanelProps {
  hasEmails: boolean;
  onImportSuccess: () => void;
}

const ImportExportPanel: React.FC<ImportExportPanelProps> = ({ hasEmails, onImportSuccess }) => {
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleExport = async (format: 'json') => {
    try {
      const response = await emailService.exportEmails(format);
      
      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `emails.${format}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }

      // Create blob URL and trigger download
      const blob = new Blob([response.data], { 
        type: 'application/json'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setSuccess(`Successfully exported emails as ${format.toUpperCase()}`);
      setError(null);
    } catch (err: any) {
      console.error('Export error:', err);
      setError(err.response?.data?.error || `Failed to export emails as ${format}`);
      setSuccess(null);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
  };

  const handleImport = async () => {
    if (!selectedFile) return;

    // Validate file extension
    const extension = selectedFile.name.split('.').pop()?.toLowerCase();
    if (!['json'].includes(extension || '')) {
      setError('Only JSON files are allowed');
      return;
    }

    setImporting(true);
    setError(null);
    setSuccess(null);

    try {
      await emailService.importEmails(selectedFile);
      setSuccess('Successfully imported emails');
      onImportSuccess();
    } catch (err: any) {
      console.error('Import error:', err.response?.data || err);
      setError(err.response?.data?.error || 'Failed to import emails');
    } finally {
      setImporting(false);
      setSelectedFile(null);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Import/Export Emails</h2>
      
      {/* Status Messages */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded">
          {success}
        </div>
      )}

      <div className="space-y-4">
        {/* Import Section - Only show when no emails */}
        {!hasEmails && (
          <div>
            <div className="flex items-center space-x-4">
              <input
                type="file"
                accept=".json"
                onChange={handleFileSelect}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
              <button
                onClick={handleImport}
                disabled={!selectedFile || importing}
                className={`px-4 py-2 rounded-md text-white ${
                  !selectedFile || importing
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-500 hover:bg-blue-600'
                }`}
              >
                {importing ? 'Importing...' : 'Import'}
              </button>
            </div>
          </div>
        )}

        {/* Export Section - Only show when there are emails */}
        {hasEmails && (
          <div>
            <div className="flex space-x-4">
              <button
                onClick={() => handleExport('json')}
                className="px-4 py-2 rounded-md bg-blue-500 text-white hover:bg-blue-600"
              >
                Export as JSON
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImportExportPanel;
