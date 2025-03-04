'use client'

import { Button } from '@/components/ui/button'
import { useLogin, usePrivy, User } from '@privy-io/react-auth'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'

export default function Home() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const { authenticated, ready, logout } = usePrivy()

  // Check if user is already authenticated and redirect
  useEffect(() => {
    if (ready && authenticated) {
      router.push('/dashboard')
    }
  }, [ready, authenticated, router])

  const { login } = useLogin({
    onComplete: async ({
      user,
      isNewUser,
      wasAlreadyAuthenticated,
      loginMethod,
    }) => {
      console.log('Login completed', {
        user,
        isNewUser,
        wasAlreadyAuthenticated,
        loginMethod,
      })
      setUser(user)

      // Redirect to dashboard after successful login
      router.push('/dashboard')
    },
  })

  return (
    <div className="grid items-center justify-items-center min-h-screen">
      {authenticated ? (
        <div className="flex flex-col gap-4">
          <p>Welcome {user?.wallet?.address}</p>
          <p>Redirecting to dashboard...</p>
          <Button variant="outline" onClick={logout}>
            Logout
          </Button>
        </div>
      ) : (
        <Button onClick={login}>Connect Wallet</Button>
      )}
    </div>
  )
}
