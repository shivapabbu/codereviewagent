'use client'

import { AlertCircle, CheckCircle, XCircle, FileText, Code, Download, Wrench } from 'lucide-react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism'

interface ReviewResultsProps {
  results: any
  onApplyFix?: (filePath: string, issue: any) => void
}

export default function ReviewResults({ results, onApplyFix }: ReviewResultsProps) {
  if (results.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="text-sm text-red-700 mt-1 whitespace-pre-wrap">{results.error}</p>
          </div>
        </div>
      </div>
    )
  }

  const issues = results.issues || []
  const missingDocs = results.missing_docstrings || []
  const score = results.overall_score || 0
  const summary = results.summary || 'No summary available'
  const fileResults = results.file_results || []
  const filesAnalyzed = results.files_analyzed || 0
  const gitInfo = results.git_info

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return <XCircle className="h-5 w-5 text-red-600" />
      case 'medium':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />
      case 'low':
        return <AlertCircle className="h-5 w-5 text-blue-600" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-600" />
    }
  }

  return (
    <div className="space-y-6 max-h-[600px] overflow-y-auto">
      {/* Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 mb-2">Summary</h3>
        <p className="text-sm text-blue-700">{summary}</p>
        {gitInfo && (
          <div className="mt-3 pt-3 border-t border-blue-300">
            <p className="text-xs text-blue-600">
              <strong>Repo:</strong> {gitInfo.repo_path} | 
              <strong> Base:</strong> {gitInfo.base_ref} | 
              <strong> Head:</strong> {gitInfo.head_ref}
            </p>
          </div>
        )}
        {filesAnalyzed > 0 && (
          <div className="mt-3 pt-3 border-t border-blue-300">
            <p className="text-xs text-blue-600">
              <strong>Files Analyzed:</strong> {filesAnalyzed}
              {results.total_files && results.total_files > filesAnalyzed && 
                ` (of ${results.total_files} found)`
              }
            </p>
          </div>
        )}
      </div>

      {/* File Results Summary (for multiple files/directory) */}
      {fileResults.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-800 mb-3">Files Summary</h3>
          <div className="max-h-48 overflow-y-auto space-y-2">
            {fileResults.map((fileResult: any, idx: number) => (
              <div key={idx} className="text-xs text-gray-700 bg-white rounded p-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono truncate flex-1">{fileResult.file_path}</span>
                  <div className="flex items-center space-x-3 ml-2">
                    <span className="text-xs">Score: {fileResult.score}/10</span>
                    {fileResult.issue_count > 0 && (
                      <span className="text-red-600">{fileResult.issue_count} issues</span>
                    )}
                    {fileResult.missing_docs_count > 0 && (
                      <span className="text-blue-600">{fileResult.missing_docs_count} missing docs</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Overall Score */}
      <div className="flex items-center justify-between bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-full ${score >= 8 ? 'bg-green-100' : score >= 5 ? 'bg-yellow-100' : 'bg-red-100'}`}>
            {score >= 8 ? (
              <CheckCircle className="h-6 w-6 text-green-600" />
            ) : (
              <AlertCircle className="h-6 w-6 text-yellow-600" />
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">Overall Score</p>
            <p className="text-xs text-gray-500">
              {score >= 8 ? 'Excellent' : score >= 5 ? 'Good' : 'Needs Improvement'}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-900">{score}/10</p>
        </div>
      </div>

      {/* Issues */}
      {issues.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <span>Issues Found ({issues.length})</span>
          </h3>
          <div className="space-y-4">
            {issues.map((issue: any, idx: number) => (
              <div
                key={idx}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    {getSeverityIcon(issue.severity)}
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded border ${getSeverityColor(
                        issue.severity
                      )}`}
                    >
                      {issue.severity?.toUpperCase() || 'UNKNOWN'}
                    </span>
                    <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                      {issue.type || 'unknown'}
                    </span>
                  </div>
                  <div className="text-right">
                    {issue.file_path && (
                      <span className="text-xs text-gray-500 block mb-1">{issue.file_path}</span>
                    )}
                    {issue.line && (
                      <span className="text-xs text-gray-500">Line {issue.line}</span>
                    )}
                  </div>
                </div>

                <p className="text-sm text-gray-700 mb-3">{issue.message}</p>

                {issue.suggestion && (
                  <div className="mt-3">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs font-medium text-gray-700">Suggestion:</p>
                      {onApplyFix && results.file_path && (
                        <button
                          onClick={() => onApplyFix(results.file_path, issue)}
                          className="text-xs text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                        >
                          <Wrench className="h-3 w-3" />
                          <span>Apply Fix</span>
                        </button>
                      )}
                    </div>
                    <div className="rounded-lg overflow-hidden border border-gray-200">
                      <SyntaxHighlighter
                        language="python"
                        style={vscDarkPlus}
                        customStyle={{ margin: 0, fontSize: '12px' }}
                      >
                        {issue.suggestion}
                      </SyntaxHighlighter>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Missing Docstrings */}
      {missingDocs.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <FileText className="h-5 w-5 text-blue-600" />
            <span>Missing Docstrings ({missingDocs.length})</span>
          </h3>
          <div className="space-y-3">
            {missingDocs.map((doc: any, idx: number) => (
              <div
                key={idx}
                className="border border-gray-200 rounded-lg p-4 bg-gray-50"
              >
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-gray-900">
                    Function: <code className="text-primary-600">{doc.function}</code>
                  </p>
                  {doc.line && (
                    <span className="text-xs text-gray-500">Line {doc.line}</span>
                  )}
                </div>
                {doc.suggestion && (
                  <div className="mt-2 rounded-lg overflow-hidden border border-gray-200">
                    <SyntaxHighlighter
                      language="python"
                      style={vscDarkPlus}
                      customStyle={{ margin: 0, fontSize: '12px' }}
                    >
                      {doc.suggestion}
                    </SyntaxHighlighter>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Issues */}
      {issues.length === 0 && missingDocs.length === 0 && (
        <div className="text-center py-8">
          <CheckCircle className="h-12 w-12 mx-auto text-green-600 mb-4" />
          <p className="text-lg font-medium text-gray-900">No Issues Found!</p>
          <p className="text-sm text-gray-500 mt-2">Your code looks good! 🎉</p>
        </div>
      )}

      {/* Download Results */}
      <div className="border-t border-gray-200 pt-4">
        <button
          onClick={() => {
            const dataStr = JSON.stringify(results, null, 2)
            const dataBlob = new Blob([dataStr], { type: 'application/json' })
            const url = URL.createObjectURL(dataBlob)
            const link = document.createElement('a')
            link.href = url
            link.download = `review_results_${new Date().toISOString()}.json`
            link.click()
          }}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          <Download className="h-4 w-4" />
          <span>Download Results as JSON</span>
        </button>
      </div>
    </div>
  )
}

