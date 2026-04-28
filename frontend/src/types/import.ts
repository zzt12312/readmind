export interface ImportJob {
  id: number | string
  file_name: string
  status: 'processing' | 'success' | 'failed'
  progress: number
  result: string
}

export interface ImportJobListResponse {
  items: ImportJob[]
}
