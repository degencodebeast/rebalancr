import { useEffect, useCallback } from 'react'
import { usePrivy } from '@privy-io/react-auth'
import { useRouter } from 'next/navigation'
import { useDispatch } from 'react-redux'
import { 
  useGetWebSocketStatusQuery, 
  useGetMessagesQuery,
  useSendMessageMutation,
  useAddLocalMessageMutation
} from '@/store/websocket/websocketApi'
import { 
  setAuthToken, 
  setUserId, 
  setShouldConnect,
  resetWebSocketState
} from '@/store/websocket/websocketSlice'

export function useWebSocketWithAuth() {
  const router = useRouter()
  const dispatch = useDispatch()
  const { user, ready, authenticated, getAccessToken } = usePrivy()
  
  // RTK Query hooks
  const { data: status } = useGetWebSocketStatusQuery()
  const { data: messages } = useGetMessagesQuery()
  const [sendMessage] = useSendMessageMutation()
  const [addLocalMessage] = useAddLocalMessageMutation()
  
  // Initialize WebSocket connection with Privy auth
  useEffect(() => {
    // Function to authenticate and connect
    const authenticateAndConnect = async () => {
      try {
        if (ready && authenticated) {
          // Get user ID from wallet address
          const userId = user?.wallet?.address
          if (userId) {
            dispatch(setUserId(userId))
          }
          
          // Get access token from Privy
          const token = await getAccessToken()
          // Store token in Redux if not null
          if (token) {
            dispatch(setAuthToken(token))
            
            // Signal to connect the WebSocket
            dispatch(setShouldConnect(true))
          }
        } else if (ready && !authenticated) {
          // Reset WebSocket state if not authenticated
          dispatch(resetWebSocketState())
        }
      } catch (error) {
        console.error('Authentication error:', error)
      }
    }
    
    authenticateAndConnect()
    
    // Cleanup on unmount
    return () => {
      dispatch(setShouldConnect(false))
    }
  }, [ready, authenticated, dispatch, getAccessToken, user?.wallet?.address])
  
  // React to authentication errors
  useEffect(() => {
    if (status?.error === 'Authentication failed') {
      // Redirect to login page on auth failure
      router.push('/')
    }
  }, [status, router])
  
  // Send chat message function
  const sendChatMessage = useCallback(async (content: string) => {
    if (!content.trim() || !status?.authenticated) return false
    
    // Create user message
    const userMessage = {
      id: `user-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      sender: 'user' as const,
      content,
      timestamp: new Date(),
    }
    
    // Add user message to local state
    await addLocalMessage(userMessage)
    
    // Send message to server
    return sendMessage({ content })
  }, [status?.authenticated, addLocalMessage, sendMessage])
  
  return {
    // Connection status
    isConnected: status?.connected || false,
    isAuthenticated: status?.authenticated || false,
    isAuthenticating: status?.authenticating || false,
    error: status?.error,
    
    // Messages
    messages: messages || [],
    
    // Actions
    sendMessage: sendChatMessage
  }
}