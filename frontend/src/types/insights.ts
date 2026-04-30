export interface TopicGraphOverview {
  topic_count: number
  cluster_count: number
  edge_count: number
  book_count: number
}

export interface TopicGraphFilterOption {
  label: string
  value: string
}

export interface TopicGraphBookOption {
  id: number
  title: string
  category: string
}

export interface TopicGraphBook {
  id: number
  title: string
  cover: string
  notes: number
}

export interface TopicGraphSample {
  note_id: number
  book_id: number
  book_title: string
  excerpt: string
}

export interface TopicClusterAction {
  label: string
  description: string
  path: string
  type: 'qa' | 'notes' | 'review'
}

export interface TopicCluster {
  id: number
  name: string
  topics: string[]
  note_count: number
  book_count: number
  sample_books: TopicGraphBook[]
  sample_excerpts: TopicGraphSample[]
  actions?: TopicClusterAction[]
}

export interface TopicGraphNode {
  id: string
  name: string
  value: number
  note_count: number
  book_count: number
  cluster_id: number
}

export interface TopicGraphLink {
  source: string
  target: string
  value: number
  co_occurrence: number
  shared_books: number
}

export interface TopicGraphPayload {
  overview: TopicGraphOverview | null
  filters: {
    selected: {
      category: string
      book_id: number | null
      time_scope: string
      mode: 'category' | 'topic'
    }
    categories: string[]
    books: TopicGraphBookOption[]
    time_scopes: TopicGraphFilterOption[]
    modes: TopicGraphFilterOption[]
  } | null
  clusters: TopicCluster[]
  graph: {
    nodes: TopicGraphNode[]
    links: TopicGraphLink[]
  }
  status?: 'queued' | 'processing' | 'success'
  job_id?: string
  message?: string
}
