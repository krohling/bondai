// app/page.tsx
import { nanoid } from '@/lib/utils'
import { Chat } from '@/components/chat'
import { redirect } from 'next/navigation'

export const runtime = 'edge'

export default function IndexPage() {
  redirect('/task')
  const id = nanoid()

  return <Chat id={id} />
}
