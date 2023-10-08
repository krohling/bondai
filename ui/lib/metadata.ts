// lib/metadata.ts

import { Metadata } from 'next'

export const metadata: Metadata = {
    title: {
      default: 'Bondai - Open source Artificial Intelligent Task Engine',
      template: `%s - Bondai`
    },
    description: 'An Open Source AI-powered Task Engine',
    themeColor: [
      { media: '(prefers-color-scheme: light)', color: 'white' },
      { media: '(prefers-color-scheme: dark)', color: 'black' }
    ],
    icons: {
      icon: '/favicon.ico',
      shortcut: '/favicon-16x16.png',
      apple: '/apple-touch-icon.png'
    }
  }