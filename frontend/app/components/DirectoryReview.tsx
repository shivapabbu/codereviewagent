'use client'

import { useState } from 'react'
import { Folder, Loader2, Search, FileText } from 'lucide-react'

interface DirectoryReviewProps {
  onReview: (directory: string, maxFiles: number) => void
  loading: boolean
}

export default function DirectoryReview({ onReview, loading }: DirectoryReviewProps) {
  const [directory, setDirectory] = useState('')
  const [maxFiles, setMaxFiles] = useState(50)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (directory.trim()) {
      onReview(directory.trim(), maxFiles)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="directory" className="block text-sm font-medium text-gray-700 mb-2">
          Directory Path
        </label>
        <div className="relative">
          <Folder className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            id="directory"
            type="text"
            value={directory}
            onChange={(e) => setDirectory(e.target.value)}
            placeholder="/path/to/your/directory"
            required
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        <p className="mt-1 text-xs text-gray-500">
          Enter the absolute path to the directory containing code files
        </p>
      </div>

      <div>
        <label htmlFor="max-files" className="block text-sm font-medium text-gray-700 mb-2">
          Maximum Files to Analyze
        </label>
        <div className="relative">
          <FileText className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            id="max-files"
            type="number"
            value={maxFiles}
            onChange={(e) => setMaxFiles(parseInt(e.target.value) || 50)}
            min="1"
            max="200"
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        <p className="mt-1 text-xs text-gray-500">
          Limit analysis to prevent excessive API calls (default: 50)
        </p>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
        <p className="text-xs text-yellow-800">
          <strong>Note:</strong> Large directories may take time. The tool will scan for common code file extensions 
          (.py, .js, .ts, .java, .cpp, .go, etc.) and skip common ignore directories (node_modules, .git, etc.).
        </p>
      </div>

      <button
        type="submit"
        disabled={loading || !directory.trim()}
        className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      >
        {loading ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Analyzing Directory...</span>
          </>
        ) : (
          <>
            <Search className="h-5 w-5" />
            <span>Analyze Directory</span>
          </>
        )}
      </button>
    </form>
  )
}

