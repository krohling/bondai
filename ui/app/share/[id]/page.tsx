// app/share/[id]/page.tsx
"use client"
import SharePageClient from './share.client'

export interface SharePageProps {
  params: {
    id: string
  }
}

export default function SharePage({ params }: SharePageProps) {
  return (
    <>     
      <SharePageClient params={params}/>
    </>
  )
}