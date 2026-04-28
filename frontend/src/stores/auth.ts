import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: {
      name: 'Tao',
      email: 'tao@example.com',
    },
  }),
})
