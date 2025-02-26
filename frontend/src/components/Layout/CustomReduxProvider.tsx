'use client'

import { store } from '@/store'
import React from 'react'
import { Provider } from 'react-redux'

export default function CustomReduxProvider({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return <Provider store={store}>{children}</Provider>
}
