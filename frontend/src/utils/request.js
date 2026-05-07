import axios from 'axios'

const request = axios.create({
  baseURL: '/weight/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

request.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('user_token')
      localStorage.removeItem('admin_token')
      localStorage.removeItem('user_info')
      localStorage.removeItem('admin_info')
      window.location.href = '/weight/'
    }
    return Promise.reject(error)
  }
)

export default request