'use client'

import { FileText, Code, Loader2, Search } from 'lucide-react'

interface CodeInputProps {
  code: string
  setCode: (code: string) => void
  filePath: string
  setFilePath: (path: string) => void
  onReview: () => void
  loading: boolean
}

export default function CodeInput({
  code,
  setCode,
  filePath,
  setFilePath,
  onReview,
  loading,
}: CodeInputProps) {
  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="file-path" className="block text-sm font-medium text-gray-700 mb-2">
          File Path (optional)
        </label>
        <div className="relative">
          <FileText className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            id="file-path"
            type="text"
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
            placeholder="e.g., src/example.py"
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      <div>
        <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
          Code
        </label>
        <div className="relative">
          <Code className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
          <textarea
            id="code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here..."
            rows={15}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
          />
        </div>
      </div>

      <button
        onClick={onReview}
        disabled={loading || !code.trim()}
        className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      >
        {loading ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Analyzing...</span>
          </>
        ) : (
          <>
            <Search className="h-5 w-5" />
            <span>Analyze Code</span>
          </>
        )}
      </button>
    </div>
  )
}

