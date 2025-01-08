import { PodcastProvider } from './context/PodcastContext'
import { ChakraProvider } from '@chakra-ui/react'
import './globals.css'

export const metadata = {
  title: 'AI Podcast Tool',
  description: 'Create AI-powered podcasts in four easy steps',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <ChakraProvider>
          <PodcastProvider>
            {children}
          </PodcastProvider>
        </ChakraProvider>
      </body>
    </html>
  )
}

