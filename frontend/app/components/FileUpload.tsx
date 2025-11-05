'use client'

import { useRef, useState } from 'react'
import { Upload, FileText, Loader2, X, Search } from 'lucide-react'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  onMultipleFilesSelect?: (files: File[]) => void
  loading: boolean
  multiple?: boolean
}

export default function FileUpload({ onFileSelect, onMultipleFilesSelect, loading, multiple = false }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files) return
    
    if (multiple && onMultipleFilesSelect) {
      const fileArray = Array.from(files)
      setSelectedFiles(fileArray)
      onMultipleFilesSelect(fileArray)
    } else if (files[0]) {
      setSelectedFile(files[0])
      onFileSelect(files[0])
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const files = e.dataTransfer.files
    if (!files.length) return
    
    if (multiple && onMultipleFilesSelect) {
      const fileArray = Array.from(files)
      setSelectedFiles(fileArray)
      onMultipleFilesSelect(fileArray)
    } else if (files[0]) {
      setSelectedFile(files[0])
      onFileSelect(files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }

  const clearFile = () => {
    setSelectedFile(null)
    setSelectedFiles([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-4">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors"
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          accept=".py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.go,.rs,.diff,.patch"
          className="hidden"
          id="file-upload"
          multiple={multiple}
        />
        
        {(selectedFile || (multiple && selectedFiles.length > 0)) ? (
          <div className="space-y-4">
            {multiple && selectedFiles.length > 0 ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-gray-900">
                    {selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} selected
                  </p>
                  <button
                    onClick={clearFile}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <div className="max-h-32 overflow-y-auto space-y-1">
                  {selectedFiles.map((file, idx) => (
                    <div key={idx} className="flex items-center space-x-2 text-sm text-gray-700">
                      <FileText className="h-4 w-4 text-primary-600" />
                      <span className="truncate">{file.name}</span>
                      <span className="text-xs text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : selectedFile ? (
              <div className="flex items-center justify-center space-x-3">
                <FileText className="h-8 w-8 text-primary-600" />
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500">
                    {(selectedFile.size / 1024).toFixed(2)} KB
                  </p>
                </div>
                <button
                  onClick={clearFile}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ) : null}
          </div>
        ) : (
          <div>
            <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <label
              htmlFor="file-upload"
              className="cursor-pointer text-primary-600 hover:text-primary-700 font-medium"
            >
              Click to upload
            </label>
            <p className="text-sm text-gray-500 mt-2">or drag and drop</p>
            <p className="text-xs text-gray-400 mt-1">
              {multiple ? 'Select multiple files' : 'Single file'} - Supports: .py, .js, .ts, .java, .cpp, .go, .rs, .diff, .patch
            </p>
          </div>
        )}
      </div>

      {((selectedFile && !multiple) || (multiple && selectedFiles.length > 0)) && !loading && !multiple && (
        <button
          onClick={() => selectedFile && onFileSelect(selectedFile)}
          className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 flex items-center justify-center space-x-2"
        >
          <Search className="h-5 w-5" />
          <span>Analyze File</span>
        </button>
      )}

      {loading && (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="h-5 w-5 animate-spin text-primary-600" />
          <span className="ml-2 text-gray-600">Analyzing file...</span>
        </div>
      )}
    </div>
  )
}

