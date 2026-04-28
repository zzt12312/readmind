import { defineStore } from 'pinia'
import { fetchNoteList } from '@/api/modules/notes'
import type { NoteFilters, NoteInsight, NoteItem, NotePagination } from '@/types/note'

const defaultInsight: NoteInsight = {
  summary: '',
  related_topics: [],
  related_note: '',
}

const defaultFilters: NoteFilters = {
  categories: [],
  tags: [],
  chapters: [],
}

const defaultPagination: NotePagination = {
  page: 1,
  per_page: 120,
  total: 0,
  total_pages: 1,
  has_more: false,
}

export const useNotesStore = defineStore('notes', {
  state: () => ({
    items: [] as NoteItem[],
    insight: defaultInsight,
    filters: defaultFilters,
    pagination: defaultPagination,
    loading: false,
    activeBookId: null as number | null,
    activeNoteId: null as number | null,
    currentFilters: {} as {
      book_id?: number
      q?: string
      note_id?: number
      category?: string
      tag?: string
      chapter?: string
      sort?: string
      page?: number
      per_page?: number
    },
  }),
  actions: {
    async load(
      filters?: {
        book_id?: number
        q?: string
        note_id?: number
        category?: string
        tag?: string
        chapter?: string
        sort?: string
        page?: number
        per_page?: number
      },
      append = false,
    ) {
      this.loading = true
      try {
        const nextFilters = { ...(append ? this.currentFilters : {}), ...(filters ?? {}) }
        this.currentFilters = nextFilters
        this.activeBookId = nextFilters.book_id ?? null
        this.activeNoteId = nextFilters.note_id ?? null
        const data = await fetchNoteList(nextFilters)
        this.items = append ? [...this.items, ...data.items] : data.items
        this.insight = data.insight
        this.filters = data.filters
        this.pagination = data.pagination
      } finally {
        this.loading = false
      }
    },
    async loadMore() {
      if (this.loading || !this.pagination.has_more) return
      await this.load(
        {
          ...this.currentFilters,
          page: this.pagination.page + 1,
        },
        true,
      )
    },
    async refreshCurrent() {
      await this.load({
        ...this.currentFilters,
        page: 1,
      })
    },
    setCurrentFilters(filters: {
      book_id?: number
      q?: string
      note_id?: number
      category?: string
      tag?: string
      chapter?: string
      sort?: string
      page?: number
      per_page?: number
    }) {
      this.currentFilters = filters
    },
  },
})
