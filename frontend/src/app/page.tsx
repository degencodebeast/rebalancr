'use client'

import { Button } from '@/components/ui/button'
import { usePrivy } from '@privy-io/react-auth'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()
  const { login, authenticated, user, logout } = usePrivy()

  return (
    <div className="grid items-center justify-items-center min-h-screen">
      {authenticated ? (
        <div className="flex flex-col gap-4">
          <p>Welcome {user?.wallet?.address}</p>
          <Button onClick={() => router.push('/websocket-test')}>
            Connection
          </Button>
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
