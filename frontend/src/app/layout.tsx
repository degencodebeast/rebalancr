import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import CustomPrivyProvider from '@/components/Layout/CustomPrivyProvider'
import CustomReduxProvider from '@/components/Layout/CustomReduxProvider'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'Rebalancr',
  description: 'Automated portfolio rebalancing',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <CustomReduxProvider>
          <CustomPrivyProvider>{children}</CustomPrivyProvider>
        </CustomReduxProvider>
      </body>
    </html>
  )
}
