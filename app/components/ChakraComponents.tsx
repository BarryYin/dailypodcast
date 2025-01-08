'use client'

import {
  Container,
  Box,
  Button,
  Textarea,
  VStack,
  useToast,
  Alert,
  AlertIcon,
} from '@chakra-ui/react'
import Link from 'next/link'
import { useEffect } from 'react'

interface ChakraComponentsProps {
  outline: string
  questions: string
  isLoading: boolean
  localScript: string
  onGenerate: () => void
  onScriptChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
}

export default function ChakraComponents({
  outline,
  questions,
  isLoading,
  localScript,
  onGenerate,
  onScriptChange,
}: ChakraComponentsProps) {
  const toast = useToast()

  useEffect(() => {
    if (!outline || !questions) {
      toast({
        title: "缺少必要内容",
        description: "请先在上一页生成大纲和问题",
        status: "warning",
        duration: 5000,
        isClosable: true,
      })
    }
  }, [outline, questions, toast])

  return (
    <Box as="main" minH="100vh" bg="gray.50">
      <Container maxW="6xl" py={8} px={4}>
        {(!outline || !questions) && (
          <Alert status="warning" mb={6}>
            <AlertIcon />
            请先在上一页生成大纲和问题
          </Alert>
        )}
        
        <VStack spacing={6} align="stretch">
          <Box>
            <Button
              onClick={onGenerate}
              isLoading={isLoading}
              loadingText="生成中..."
              colorScheme="green"
              size="lg"
              mb={4}
              isDisabled={!outline || !questions}
            >
              生成播客文字稿
            </Button>
          </Box>

          <Box bg="white" rounded="xl" shadow="lg" p={6}>
            <Textarea
              value={localScript}
              onChange={onScriptChange}
              placeholder="点击"生成播客文字稿"按钮，生成对话内容..."
              minH="500px"
              p={4}
              fontSize="lg"
              isDisabled={!outline || !questions}
            />
          </Box>

          <Box display="flex" justifyContent="space-between" mt={4}>
            <Link href="/content-outline" passHref>
              <Button as="a" colorScheme="gray" size="lg">
                上一步
              </Button>
            </Link>
            <Link href="/audio-generation" passHref>
              <Button
                as="a"
                colorScheme="blue"
                size="lg"
                isDisabled={!localScript.trim()}
              >
                下一步
              </Button>
            </Link>
          </Box>
        </VStack>
      </Container>
    </Box>
  )
} 