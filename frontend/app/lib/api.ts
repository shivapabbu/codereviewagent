import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ReviewResponse {
  summary?: string
  issues?: Array<{
    type: string
    severity: string
    line?: number
    message: string
    suggestion?: string
  }>
  missing_docstrings?: Array<{
    function: string
    line?: number
    suggestion?: string
  }>
  overall_score?: number
  file_path?: string
  error?: string
}

export async function analyzeCode(code: string, filePath?: string): Promise<ReviewResponse> {
  try {
    const response = await api.post<ReviewResponse>('/api/review/code', {
      code,
      file_path: filePath,
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to analyze code')
  }
}

export async function analyzeFile(file: File): Promise<ReviewResponse> {
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post<ReviewResponse>('/api/review/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to analyze file')
  }
}

export async function analyzeFilePath(filePath: string): Promise<ReviewResponse> {
  try {
    const formData = new FormData()
    formData.append('file_path', filePath)
    
    const response = await api.post<ReviewResponse>('/api/review/file-path', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to analyze file')
  }
}

export async function applyFix(filePath: string, issue: any): Promise<void> {
  try {
    await api.post('/api/fix/apply', {
      file_path: filePath,
      issue,
    })
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to apply fix')
  }
}

export async function getRecentResults(limit: number = 10) {
  try {
    const response = await api.get(`/api/results?limit=${limit}`)
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get results')
  }
}

export async function analyzeGitRepo(repoPath: string, baseRef?: string, headRef?: string): Promise<ReviewResponse> {
  try {
    const response = await api.post<ReviewResponse>('/api/review/git', {
      repo_path: repoPath,
      base_ref: baseRef,
      head_ref: headRef,
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to analyze git repository')
  }
}

export async function analyzeDirectory(directory: string, maxFiles: number = 50): Promise<ReviewResponse> {
  try {
    const response = await api.post<ReviewResponse>('/api/review/directory', {
      directory,
      max_files: maxFiles,
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to analyze directory')
  }
}

export async function analyzeMultipleFiles(files: File[]): Promise<ReviewResponse> {
  try {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    
    const response = await api.post<ReviewResponse>('/api/review/multiple-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to analyze multiple files')
  }
}

export async function listCodeFiles(directory: string, extensions?: string) {
  try {
    const params = new URLSearchParams({ directory })
    if (extensions) {
      params.append('extensions', extensions)
    }
    const response = await api.get(`/api/files/list?${params.toString()}`)
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to list files')
  }
}

