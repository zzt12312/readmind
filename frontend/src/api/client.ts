import axios from 'axios'

export const apiClient = axios.create({
  // 生产环境默认走同源 /api，这样静态站部署到任意域名或 IP 后都能直接通过 Nginx 反代访问后端。
  // 本地开发如果需要独立后端地址，仍然可以通过 VITE_API_BASE_URL 覆盖。
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 10000,
})
