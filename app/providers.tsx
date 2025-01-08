'use client';

import { CacheProvider } from '@chakra-ui/next-js'
import { ChakraProvider } from '@chakra-ui/react';
import { PodcastContextProvider } from './context/PodcastContext';
import theme from './theme';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <CacheProvider>
      <ChakraProvider theme={theme}>
        <PodcastContextProvider>
          {children}
        </PodcastContextProvider>
      </ChakraProvider>
    </CacheProvider>
  );
} 