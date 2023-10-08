// components/header.tsx
'use client';
import * as React from 'react'
import Link from 'next/link'

import { cn } from '@/lib/utils'
import { Button, buttonVariants } from '@/components/ui/button'
import { Sidebar } from '@/components/sidebar'
import { SidebarList } from '@/components/sidebar-list'
import {
  IconGitHub,
  IconNextChat,
  IconDiscord
} from '@/components/ui/icons'
import { SidebarFooter } from '@/components/sidebar-footer'
import { ThemeToggle } from '@/components/theme-toggle'
import { UserMenu } from '@/components/user-menu'
import { useChatContext } from '@/lib/hooks/use-chat-context';

const userId = "ABC123"

export function Header() {
  const { chats, setChats } = useChatContext();

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between w-full h-16 px-4 border-b shrink-0 bg-gradient-to-b from-background/10 via-background/50 to-background/80 backdrop-blur-xl">
      <div className="flex items-center">
        {userId ? (
          <Sidebar>
            <React.Suspense fallback={<div className="flex-1 overflow-auto" />}>
              {/* @ts-ignore */}
              <SidebarList userId={userId} chats={chats} setChats={setChats} />
            </React.Suspense>
            <SidebarFooter userId={userId} chats={chats} setChats={setChats}>
              <ThemeToggle />
            </SidebarFooter>
          </Sidebar>
        ) : (
          <Link href="/" target="_blank" rel="nofollow">
            <IconNextChat className="w-6 h-6 mr-2 dark:hidden" inverted />
            <IconNextChat className="hidden w-6 h-6 mr-2 dark:block" />
          </Link>
        )}
        <div className="flex items-center">
          <Link href="/">
            <img src="/bondai-logo.png" alt="Bondai Logo" className="h-[25px] w-auto ml-2" />
          </Link>
        </div>
      </div>
      <div className="flex items-center justify-end space-x-2">
        <a
          target="_blank"
          href="https://github.com/krohling/bondai"
          rel="noopener noreferrer"
          className={cn(buttonVariants({ variant: 'outline' }))}
        >
          <IconGitHub />
          <span className="ml-2 md:flex">GitHub</span>
        </a>
        <a
          href="https://discord.gg/hXY4r5FFb"
          target="_blank"
          className={cn(buttonVariants())}
        >
          <IconDiscord className="mr-2" />
          <span className="sm:block">Discord</span>
        </a>
      </div>
    </header>
  )
}
