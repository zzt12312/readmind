import axios, { AxiosError, type AxiosAdapter, type AxiosResponse } from 'axios'
import { isStaticDemoMode } from '@/config/demo'

const staticDemoAdapter: AxiosAdapter = async (config) => {
  const { resolveStaticDemoResponse } = await import('@/mock/staticDemo')
  const data = resolveStaticDemoResponse(config)
  const response = {
    data: data ?? {
      error: {
        code: 'STATIC_DEMO_NOT_FOUND',
        message: '静态演示模式暂不支持这个接口',
      },
    },
    status: data ? 200 : 404,
    statusText: data ? 'OK' : 'Not Found',
    headers: {},
    config,
  } as AxiosResponse

  if (!data) {
    return Promise.reject({
      isAxiosError: true,
      response,
      config,
      message: response.data.error.message,
      name: 'AxiosError',
    })
  }

  return response
}

export const apiClient = axios.create({
  // 生产环境默认走同源 /api，这样静态站部署到任意域名或 IP 后都能直接通过 Nginx 反代访问后端。
  // 本地开发如果需要独立后端地址，仍然可以通过 VITE_API_BASE_URL 覆盖。
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 10000,
  adapter: isStaticDemoMode ? staticDemoAdapter : undefined,
})

interface ApiErrorPayload {
  error?: {
    code?: string
    message?: string
    detail?: string
  }
}

export class ApiError extends Error {
  code: string
  detail: string
  status?: number

  constructor(message: string, code = 'REQUEST_FAILED', detail = '', status?: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.detail = detail
    this.status = status
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorPayload>) => {
    const payload = error.response?.data?.error
    if (payload) {
      return Promise.reject(
        new ApiError(
          payload.message || '请求失败',
          payload.code || 'REQUEST_FAILED',
          payload.detail || '',
          error.response?.status,
        ),
      )
    }
    return Promise.reject(error)
  },
)
