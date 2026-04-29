import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: {
      name: '本地用户',
      email: '',
    },
  }),
})
