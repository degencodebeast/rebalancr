import { useEffect, useRef, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector, useDispatch } from 'react-redux'
import { 
  startVerifying, 
  verificationSuccess, 
  verificationFailed, 
  selectIsVerifying,
  selectVerificationError,
  selectHasVerified
} from '@/store/auth/authSlice'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'

export function useWebSocketAuth() {
  const dispatch = useDispatch()
  const router = useRouter()
  const wsRef = useRef<WebSocket | null>(null)
  const isVerifying = useSelector(selectIsVerifying)
  const verificationError = useSelector(selectVerificationError)
  const hasVerified = useSelector(selectHasVerified)
  
  // Setup WebSocket connection for authentication
  useEffect(() => {
    // Only establish the WebSocket once
    if (wsRef.current) {
      return;
    }
    
    // Create WebSocket connection
    const ws = new WebSocket(WS_URL)
    wsRef.current = ws
    
    // Handle connection events
    ws.onopen = () => {
      console.log('WebSocket connected for authentication')
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        // Authentication success - redirect to dashboard
        if (data.type === 'auth_success') {
          console.log('Authentication successful')
          dispatch(verificationSuccess())
          router.push('/dashboard')
        } 
        // Authentication failure - show error
        else if (data.type === 'auth_failed') {
          console.error('Authentication failed:', data.error)
          dispatch(verificationFailed(data.error || 'Authentication failed'))
        }
      } catch (error) {
        console.error('Error parsing message:', error)
      }
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
      wsRef.current = null
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      dispatch(verificationFailed('Connection error'))
    }
    
    // Cleanup on unmount
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [dispatch, router])
  
  // Function to authenticate with token
  const authenticateWithToken = useCallback(async (token: string, userId?: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      dispatch(verificationFailed('WebSocket not connected'))
      return false
    }
    
    try {
      dispatch(startVerifying())
      
      // Send authentication message
      wsRef.current.send(JSON.stringify({
        type: 'auth',
        token,
        userId
      }))
      
      return true
    } catch (error) {
      console.error('Error sending authentication:', error)
      dispatch(verificationFailed('Failed to send authentication'))
      return false
    }
  }, [dispatch])
  
  return {
    authenticateWithToken,
    isVerifying,
    verificationError,
    hasVerified
  }
} 