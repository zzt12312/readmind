export interface ImportJob {
  id: number | string
  file_name: string
  status: 'processing' | 'success' | 'failed'
  progress: number
  result: string
}

export interface ImportMeta {
  demo_mode: boolean
  source_label: string
  description: string
}

export interface ImportJobListResponse {
  items: ImportJob[]
  meta: ImportMeta
}
