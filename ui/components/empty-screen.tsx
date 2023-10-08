import { UseChatHelpers } from 'ai/react'

import { Button } from '@/components/ui/button'
import { ExternalLink } from '@/components/external-link'
import { IconArrowRight } from '@/components/ui/icons'

const exampleMessages = [
  {
    heading: `Turn my lights off`,
    message: `Find smart light bulbs on my home network and turn them off.`
  },
  {
    heading: `Order me a Pizza`,
    message: `Im hungry! Order me a regular cheese pizza to be delivered tonight at 8pm from Dominos on 250-123-4567 to be delivered at my home address 123 Park Blvd, Dallas, TX, 65123.`
  },
  {
    heading: `Send my Mom some flowers`,
    message: `My Mom's birthday is next Tuesday; Buy her some flowers for $30 and add a note "Happy Birthday Mom, love from Bondai".`
  }
]

export function EmptyScreen({ setInput }: Pick<UseChatHelpers, 'setInput'>) {
  return (
    <div className="mx-auto max-w-2xl px-4">
      <div className="rounded-lg border bg-background p-8">
        <h1 className="mb-2 text-lg font-semibold">
          Welcome to Bondai
        </h1>
        <p className="mb-2 leading-normal text-muted-foreground">
          An open source Artificial Intelligent Task Engine.
        </p>
        <p className="mb-2 leading-normal text-muted-foreground">
          Connect to your existing project with an extensible API {' '}
          and expand it&apos;s capabilities with our Ai Toolset.
        </p>
        <p className="mt-8 leading-normal text-muted-foreground">
          Check it out with some example task prompts..
        </p>
        <div className="mt-4 flex flex-col items-start space-y-2">
          {exampleMessages.map((message, index) => (
            <Button
              key={index}
              variant="link"
              className="h-auto p-0 text-base"
              onClick={() => setInput(message.message)}
            >
              <IconArrowRight className="mr-2 text-muted-foreground" />
              {message.heading}
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}
