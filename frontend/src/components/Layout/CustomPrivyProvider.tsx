'use client'

import { PrivyProvider } from '@privy-io/react-auth'
import { monadTestnet } from 'viem/chains'

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <PrivyProvider
      appId={process.env.NEXT_PUBLIC_PRIVY_APP_ID!}
      config={{
        appearance: {
          theme: 'light',
          accentColor: '#676FFF',
          logo: 'https://your-logo-url',
          walletList: [
            'phantom',
            'metamask',
            'coinbase_wallet',
            'rabby_wallet',
            'rainbow',
            'wallet_connect',
            'backpack',
          ],
        },

        defaultChain: monadTestnet,
        supportedChains: [monadTestnet],
      }}
    >
      {children}
    </PrivyProvider>
  )
}
