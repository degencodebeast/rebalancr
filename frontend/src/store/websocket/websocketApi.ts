import { createApi } from '@reduxjs/toolkit/query/react'

declare global {
  interface Window {
    WebSocket: typeof WebSocket
  }
}

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || ''
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
          ws = new WebSocket(WS_URL)

          ws.onerror = (error) => {
            console.error('WebSocket error:', error)
          }

          ws.onopen = () => {
            console.log('WebSocket connected')
            ws?.send(JSON.stringify({ type: 'get_portfolio' }))
          }

          ws.onmessage = (event) => {
            const data = JSON.parse(event.data)
            updateCachedData((draft) => {
              if (!Array.isArray(draft)) {
                return [data]
              }
              draft.push(data)
            })
          }

          ws.onclose = (event) => {
            console.log('WebSocket closed:', event.reason)
            // Try to reconnect
            retryTimeout = setTimeout(() => {
              console.log('Attempting to reconnect...')
              createWebSocketConnection()
            }, RECONNECT_INTERVAL)
          }
        }

        try {
          await cacheDataLoaded
          createWebSocketConnection()
        } catch (err) {
          console.error('WebSocket error:', err)
        }

        // Cleanup function
        await cacheEntryRemoved
        clearTimeout(retryTimeout)
        if (ws) {
          ;(ws as any).close()
        }
      },
    }),
  }),
})

export const { useGetWebSocketMessagesQuery } = websocketApi
