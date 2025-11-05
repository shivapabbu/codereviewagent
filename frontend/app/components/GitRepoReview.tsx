'use client'

import { useState } from 'react'
import { GitBranch, Loader2, Search, Folder } from 'lucide-react'

interface GitRepoReviewProps {
  onReview: (repoPath: string, baseRef?: string, headRef?: string) => void
  loading: boolean
}

export default function GitRepoReview({ onReview, loading }: GitRepoReviewProps) {
  const [repoPath, setRepoPath] = useState('')
  const [baseRef, setBaseRef] = useState('')
  const [headRef, setHeadRef] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (repoPath.trim()) {
      onReview(repoPath.trim(), baseRef.trim() || undefined, headRef.trim() || undefined)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="repo-path" className="block text-sm font-medium text-gray-700 mb-2">
          Git Repository Path
        </label>
        <div className="relative">
          <Folder className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            id="repo-path"
            type="text"
            value={repoPath}
            onChange={(e) => setRepoPath(e.target.value)}
            placeholder="/path/to/your/repo"
            required
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        <p className="mt-1 text-xs text-gray-500">
          Enter the absolute path to your git repository
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="base-ref" className="block text-sm font-medium text-gray-700 mb-2">
            Base Reference (optional)
          </label>
          <div className="relative">
            <GitBranch className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              id="base-ref"
              type="text"
              value={baseRef}
              onChange={(e) => setBaseRef(e.target.value)}
              placeholder="main, HEAD, commit-hash"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <p className="mt-1 text-xs text-gray-500">Base branch/commit</p>
        </div>

        <div>
          <label htmlFor="head-ref" className="block text-sm font-medium text-gray-700 mb-2">
            Head Reference (optional)
          </label>
          <div className="relative">
            <GitBranch className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              id="head-ref"
              type="text"
              value={headRef}
              onChange={(e) => setHeadRef(e.target.value)}
              placeholder="feature-branch, commit-hash"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <p className="mt-1 text-xs text-gray-500">Compare branch/commit</p>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-xs text-blue-800">
          <strong>Tip:</strong> Leave both refs empty to review unstaged changes. 
          Use base/head to compare branches or commits.
        </p>
      </div>

      <button
        type="submit"
        disabled={loading || !repoPath.trim()}
        className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      >
        {loading ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Analyzing Repository...</span>
          </>
        ) : (
          <>
            <Search className="h-5 w-5" />
            <span>Analyze Git Repository</span>
          </>
        )}
      </button>
    </form>
  )
}

