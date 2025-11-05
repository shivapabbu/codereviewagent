'use client'

import { useState } from 'react'
import { Search, Upload, FileText, AlertCircle, CheckCircle, XCircle, Loader2, GitBranch, Folder } from 'lucide-react'
import CodeInput from './components/CodeInput'
import FileUpload from './components/FileUpload'
import GitRepoReview from './components/GitRepoReview'
import DirectoryReview from './components/DirectoryReview'
import ReviewResults from './components/ReviewResults'
import { analyzeCode, analyzeFile, analyzeGitRepo, analyzeDirectory, analyzeMultipleFiles, applyFix } from './lib/api'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'code' | 'file' | 'multiple' | 'git' | 'directory'>('code')
  const [code, setCode] = useState('')
  const [filePath, setFilePath] = useState('')
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCodeReview = async () => {
    if (!code.trim()) {
      setError('Please enter some code to review')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const data = await analyzeCode(code, filePath || undefined)
      setResults(data)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze code')
    } finally {
      setLoading(false)
    }
  }

  const handleFileReview = async (file: File) => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const data = await analyzeFile(file)
      setResults(data)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze file')
    } finally {
      setLoading(false)
    }
  }

  const handleMultipleFilesReview = async (files: File[]) => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const data = await analyzeMultipleFiles(files)
      setResults(data)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze files')
    } finally {
      setLoading(false)
    }
  }

  const handleGitRepoReview = async (repoPath: string, baseRef?: string, headRef?: string) => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const data = await analyzeGitRepo(repoPath, baseRef, headRef)
      setResults(data)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze git repository')
    } finally {
      setLoading(false)
    }
  }

  const handleDirectoryReview = async (directory: string, maxFiles: number) => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const data = await analyzeDirectory(directory, maxFiles)
      setResults(data)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze directory')
    } finally {
      setLoading(false)
    }
  }

  const handleApplyFix = async (filePath: string, issue: any) => {
    try {
      await applyFix(filePath, issue)
      // Optionally refresh the review
      alert('Fix applied successfully!')
    } catch (err: any) {
      alert(`Failed to apply fix: ${err.message}`)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Search className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  AWS Bedrock Code Review Agent
                </h1>
                <p className="text-sm text-gray-500">
                  AI-powered code review using Claude via AWS Bedrock
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-sm text-gray-600">API Connected</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-4 px-6 overflow-x-auto" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('code')}
                className={`${
                  activeTab === 'code'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
              >
                <FileText className="h-5 w-5" />
                <span>Code Input</span>
              </button>
              <button
                onClick={() => setActiveTab('file')}
                className={`${
                  activeTab === 'file'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
              >
                <Upload className="h-5 w-5" />
                <span>Single File</span>
              </button>
              <button
                onClick={() => setActiveTab('multiple')}
                className={`${
                  activeTab === 'multiple'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
              >
                <FileText className="h-5 w-5" />
                <span>Multiple Files</span>
              </button>
              <button
                onClick={() => setActiveTab('git')}
                className={`${
                  activeTab === 'git'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
              >
                <GitBranch className="h-5 w-5" />
                <span>Git Repo</span>
              </button>
              <button
                onClick={() => setActiveTab('directory')}
                className={`${
                  activeTab === 'directory'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
              >
                <Folder className="h-5 w-5" />
                <span>Directory</span>
              </button>
            </nav>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-600 hover:text-red-800"
            >
              <XCircle className="h-5 w-5" />
            </button>
          </div>
        )}

        {/* Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {activeTab === 'code' ? 'Enter Code' : 
               activeTab === 'file' ? 'Upload Single File' :
               activeTab === 'multiple' ? 'Upload Multiple Files' :
               activeTab === 'git' ? 'Analyze Git Repository' :
               'Analyze Directory'}
            </h2>
            
            {activeTab === 'code' ? (
              <CodeInput
                code={code}
                setCode={setCode}
                filePath={filePath}
                setFilePath={setFilePath}
                onReview={handleCodeReview}
                loading={loading}
              />
            ) : activeTab === 'file' ? (
              <FileUpload
                onFileSelect={handleFileReview}
                loading={loading}
              />
            ) : activeTab === 'multiple' ? (
              <FileUpload
                onFileSelect={handleFileReview}
                onMultipleFilesSelect={handleMultipleFilesReview}
                loading={loading}
                multiple={true}
              />
            ) : activeTab === 'git' ? (
              <GitRepoReview
                onReview={handleGitRepoReview}
                loading={loading}
              />
            ) : (
              <DirectoryReview
                onReview={handleDirectoryReview}
                loading={loading}
              />
            )}
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Review Results
            </h2>
            
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 text-primary-600 animate-spin" />
                <span className="ml-3 text-gray-600">Analyzing code with AWS Bedrock...</span>
              </div>
            ) : results ? (
              <ReviewResults
                results={results}
                onApplyFix={handleApplyFix}
              />
            ) : (
              <div className="text-center py-12 text-gray-500">
                <Search className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Enter code or upload a file to get started</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            Powered by AWS Bedrock & Claude 3
          </p>
        </div>
      </footer>
    </div>
  )
}

