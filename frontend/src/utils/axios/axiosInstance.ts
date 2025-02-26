import axios from 'axios'
import { setupInterceptors } from './interceptors'

const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

setupInterceptors(axiosInstance)

export default axiosInstance
