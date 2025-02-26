import {
  AxiosInstance,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios'
import { toast } from 'react-toastify'

// Function to set up interceptors
export const setupInterceptors = (axiosInstance: AxiosInstance) => {
  // Request Interceptor
  axiosInstance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // Add logic to modify the request before it is sent
      // For example, attach an Authorization header
      const token = localStorage.getItem('accessToken') // Or wherever your token is stored
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }

      console.log('[Request]', config) // For debugging purposes
      return config
    },
    (error: AxiosError) => {
      // Handle errors that occur before the request is sent
      console.error('[Request Error]', error)
      return Promise.reject(error)
    },
  )

  // Response Interceptor
  axiosInstance.interceptors.response.use(
    (response: AxiosResponse) => {
      // Modify the response or just return it
      console.log('[Response]', response) // For debugging purposes
      return response
    },
    (error: AxiosError) => {
      // Handle errors returned by the server
      console.error('[Response Error]', error)

      // Optionally, handle specific error status codes globally
      if (error.response) {
        const { status } = error.response
        if (status === 401) {
          // Example: Redirect to login page on unauthorized response
          window.location.href = '/'
        } else if (status === 403) {
          toast('You do not have permission to perform this action.', {
            type: 'error',
          })
          window.location.href = '/'
        } else if (status >= 500) {
          toast('An error occurred on the server. Please try again later.', {
            type: 'error',
          })
        }
      }

      return Promise.reject(error)
    },
  )
}
