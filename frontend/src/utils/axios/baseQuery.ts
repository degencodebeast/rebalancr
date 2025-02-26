import { BaseQueryFn } from '@reduxjs/toolkit/query'
import { AxiosError, AxiosRequestConfig } from 'axios'
import axiosInstance from './axiosInstance'

// Define the custom base query function
export const axiosBaseQuery =
  (): BaseQueryFn<
    {
      url: string
      method: AxiosRequestConfig['method']
      data?: AxiosRequestConfig['data']
      params?: AxiosRequestConfig['params']
      headers?: AxiosRequestConfig['headers']
    },
    unknown,
    unknown
  > =>
  async ({ url, method, data, params, headers }) => {
    try {
      // Get the access token from localStorage
      const token = localStorage.getItem('accessToken')

      // Perform the Axios request
      const result = await axiosInstance({
        url,
        method,
        data,
        params,
        headers: {
          ...headers, // Include any headers passed explicitly
          ...(token ? { Authorization: `Bearer ${token}` } : {}), // Add Authorization header if token exists
        },
      })

      // Save token to localStorage if it's part of the response
      if (result.data?.accessToken) {
        const token = result.data.accessToken
        localStorage.setItem('accessToken', token)
      }

      // Return the result as required by RTK Query
      return { data: result.data }
    } catch (axiosError) {
      const error = axiosError as AxiosError

      if (error.response?.status === 401) {
        // Clear the expired token
        localStorage.removeItem('accessToken')

        // Optional: Redirect to login page
        window.location.href = '/'
      }

      return {
        error: {
          status: error.response?.status || 'FETCH_ERROR',
          data: error.response?.data || error.message,
        },
      }
    }
  }
