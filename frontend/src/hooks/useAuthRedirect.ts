'use client'

import { usePrivy, useLogin } from '@privy-io/react-auth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export const useAuthRedirect = () => {
  const router = useRouter()
  const { authenticated, ready } = usePrivy()

  // Check if user is already authenticated and redirect
  useEffect(() => {
    if (ready && authenticated) {
      router.push('/dashboard')
    }
  }, [ready, authenticated, router])

  const { login } = useLogin({
    onComplete: async () => {
      // Redirect to dashboard after successful login
      router.push('/dashboard')
    },
  })

  return { login, authenticated, ready }
}
