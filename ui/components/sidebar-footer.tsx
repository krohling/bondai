// components/sidebar-footer.tsx
import { cn } from '@/lib/utils'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ClearHistory } from '@/components/clear-history'
import { Chat } from '@/lib/types';

interface SidebarFooterProps extends React.ComponentProps<'div'> {
  userId: string;
  chats: Chat[] | null;
  setChats: React.Dispatch<React.SetStateAction<Chat[] | null>>;
}

export function SidebarFooter({
  userId,
  chats,
  setChats,
  children,
  className,
  ...props
}: SidebarFooterProps) {
  const router = useRouter()

  const handleClearChats = async (): Promise<void> => {

    const res = await fetch(`${window.location.origin}/api/clearChats`, {
      method: 'POST',
      body: JSON.stringify({ userId }),
    });
    
    if (res.ok) {
      setChats([]);
    }
  };

  return (
    <div
      className={cn('flex items-center justify-between p-4', className)}
      {...props}
    >
      {children}

      <Button onClick={e => {
          e.preventDefault()
          router.refresh()
          router.push('/')
        }} variant="ghost" className="border dark:border-white/20 dark:text-white dark:hover:bg-white text-xs hover:text-black">
        New Chat
      </Button>
      <ClearHistory clearChats={handleClearChats} />
    </div>
  )
}
