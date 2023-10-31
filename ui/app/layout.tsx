// app/layout.tsx

import { Metadata } from 'next'
import { Toaster } from 'react-hot-toast'
import '@/app/globals.css'
import { fontMono, fontSans } from '@/lib/fonts'
import { cn } from '@/lib/utils'
import { Providers } from '@/components/providers'
import { Header } from '@/components/header'
import ChatLayout from '@/components/chat-layout';

export const metadata: Metadata = {
  title: {
    default: 'Bondai - Open Source Artificial Intelligent Task Engine',
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

interface RootLayoutProps {
  children: React.ReactNode
}

export default function RootLayout({ children }: RootLayoutProps) {

  return (
    <ChatLayout>
      <html lang="en" suppressHydrationWarning>
        <head />
        <body
          className={cn(
            'dark:bg-bondai',
            'font-sans antialiased',
            fontSans.variable,
            fontMono.variable
          )}
        >
          <Toaster />
          <Providers attribute="class" defaultTheme="system" enableSystem>
            <div className="flex flex-col min-h-screen">
              {/* @ts-ignore */}
              <Header />
              <main className="flex flex-col flex-1 bg-muted/50">{children}</main>
            </div>
          </Providers>
        </body>
      </html>
    </ChatLayout>
  )
}
