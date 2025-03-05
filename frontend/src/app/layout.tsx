import type { Metadata } from 'next'
import { Bricolage_Grotesque, Outfit } from 'next/font/google'
import './globals.scss'
import '@mantine/core/styles.css'
import CustomPrivyProvider from '@/components/Layout/CustomPrivyProvider'
import CustomReduxProvider from '@/components/Layout/CustomReduxProvider'
import {
  ColorSchemeScript,
  MantineProvider,
  mantineHtmlProps,
} from '@mantine/core'

const bricolageGrotesque = Bricolage_Grotesque({
  subsets: ['latin'],
})

const outfit = Outfit({
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
    <html lang="en" {...mantineHtmlProps}>
      <head>
        <ColorSchemeScript />
      </head>
      <body
        className={`${bricolageGrotesque.className} ${outfit.className} antialiased`}
      >
        <CustomReduxProvider>
          <MantineProvider
            theme={{
              colors: {
                custom: [
                  '#f2f2f2',
                  '#e6e6e6',
                  '#cccccc',
                  '#b3b3b3',
                  '#999999',
                  '#808080',
                  '#666666',
                  '#4d4d4d',
                  '#333333',
                  '#1a1a1a',
                ],
              },
              primaryColor: 'custom',
            }}
          >
            <CustomPrivyProvider>{children}</CustomPrivyProvider>
          </MantineProvider>
        </CustomReduxProvider>
      </body>
    </html>
  )
}
