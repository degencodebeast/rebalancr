import { createApi } from '@reduxjs/toolkit/query/react'

declare global {
  interface Window {
    WebSocket: typeof WebSocket
  }
}

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
const RECONNECT_INTERVAL = 5000 // 5 seconds

export const websocketApi = createApi({
  reducerPath: 'websocketApi',
  baseQuery: () => ({ data: null }),
  endpoints: (builder) => ({
    getWebSocketMessages: builder.query<any, void>({
      queryFn: () => ({ data: null }),
      async onCacheEntryAdded(
        _arg,
        { updateCachedData, cacheDataLoaded, cacheEntryRemoved },
      ) {
        let ws: WebSocket | null = null
        let retryTimeout: NodeJS.Timeout | undefined

        // Function to create WebSocket connection
        const createWebSocketConnection = () => {
          console.log('Creating WebSocket connection to:', WS_URL)
          
          if (!WS_URL) {
            console.error('WebSocket URL is empty or undefined')
            return
          }
          
          ws = new WebSocket(WS_URL)

          ws.onerror = (error) => {
            console.error('WebSocket error:', error)
          }

          ws.onopen = () => {
            console.log('WebSocket connected successfully!')
            // Send an initial message after connecting
            ws?.send(JSON.stringify({ type: 'connect', message: 'Initial connection' }))
          }

          ws.onmessage = (event) => {
            // const data = JSON.parse(event.data)
            // updateCachedData((draft) => {
            //   if (!Array.isArray(draft)) {
            //     return [data]
            //   }
            //   draft.push(data)
            // })
            console.log('WebSocket message received:', event.data)
            try {
              const data = JSON.parse(event.data)
              updateCachedData((draft) => {
                // Handle the case where draft is null or not an array
                if (!Array.isArray(draft)) {
                  // With immer, we need to modify the draft directly
                  return [data]
                }
                draft.push(data)
              })
            } catch (error) {
              console.error('Error parsing WebSocket message:', error)
            }
          }

          ws.onclose = (event) => {
            console.log('WebSocket closed. Code:', event.code, 'Reason:', event.reason)
            // Try to reconnect
            retryTimeout = setTimeout(() => {
              console.log('Attempting to reconnect WebSocket...')
              createWebSocketConnection()
            }, RECONNECT_INTERVAL)
          }
        }

        try {
          await cacheDataLoaded
          createWebSocketConnection()
        } catch (err) {
          console.error('WebSocket initialization error:', err)
        }

        // Cleanup function
        await cacheEntryRemoved
        console.log('Cleaning up WebSocket connection')
        clearTimeout(retryTimeout)
        if (ws) {
          ;(ws as any).close()
        }
        // if (ws && ws.readyState !== WebSocket.CLOSED) {
        //   console.log('Closing WebSocket connection')
        //   ws.close()
        // }
      },
    }),
    sendWebSocketMessage: builder.mutation<void, any>({
      queryFn: (message) => {
        const ws = new WebSocket(WS_URL)
        
        return new Promise((resolve, reject) => {
          ws.onopen = () => {
            ws.send(JSON.stringify(message))
            ws.close()
            resolve({ data: undefined })
          }
          
          ws.onerror = (error) => {
            reject(error)
          }
        })
      }
    }),
  }),
})

export const { useGetWebSocketMessagesQuery, useSendWebSocketMessageMutation } = websocketApi
