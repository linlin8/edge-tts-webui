import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
})

// 响应拦截：解包 ResponseBase
client.interceptors.response.use(
  (response) => {
    const { code, msg, data } = response.data
    if (code !== 0) {
      const err = new Error(msg || '请求失败')
      err.code = code
      err.data = data
      return Promise.reject(err)
    }
    return data
  },
  (error) => {
    const msg = error.response?.data?.msg || '网络异常，请稍后重试'
    const err = new Error(msg)
    err.code = error.response?.status || -1
    return Promise.reject(err)
  }
)

// 具名导出供组件直接使用
export const apiClient = client
export default client
