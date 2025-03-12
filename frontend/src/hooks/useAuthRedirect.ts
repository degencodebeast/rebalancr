'use client'

import { usePrivy, useLogin } from '@privy-io/react-auth'
import { useEffect } from 'react'
import { useWebSocketAuth } from './useWebSocketAuth'

export const useAuthRedirect = () => {
  const { authenticated, ready, getAccessToken, user } = usePrivy()
  const { authenticateWithToken, isVerifying, verificationError, hasVerified } = useWebSocketAuth()
  
  // Attempt to authenticate with WebSocket when Privy is authenticated
  useEffect(() => {
    const authenticate = async () => {
      if (ready && authenticated && !isVerifying && !hasVerified) {
        try {
          // Get token from Privy
          const token = await getAccessToken()
          const userId = user?.wallet?.address ?? ''
          
          // Only proceed if we have a valid token
          if (token) {
            // Authenticate via WebSocket
            await authenticateWithToken(token, userId || undefined)
          }
          else {
            console.error('No authentication token available')
          }
        } catch (error) {
          console.error('Error getting access token:', error)
        }
      }
    }
    
    authenticate()
  }, [ready, authenticated, isVerifying, hasVerified, getAccessToken, authenticateWithToken, user?.wallet?.address])

  const { login } = useLogin({
    onComplete: async () => {
      // Authentication and redirect will be handled by the useEffect above
    },
  })

  return { 
    login, 
    authenticated, 
    ready, 
    isVerifying,
    verificationError 
  }
}
