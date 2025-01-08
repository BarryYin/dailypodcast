'use client'

import { useState, useEffect } from 'react'
import { usePodcastContext } from '../context/PodcastContext'
import { generateScript } from '../utils/api'
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

export default function PodcastGenerationContent() {
  const { outline, questions } = usePodcastContext()
  const [isLoading, setIsLoading] = useState(false)
  const [localScript, setLocalScript] = useState('')
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

  const handleGenerateScript = async () => {
    if (!outline || !questions) {
      toast({
        title: "无法生成",
        description: "请确保已经生成了大纲和问题",
        status: "error",
        duration: 3000,
        isClosable: true,
      })
      return
    }

    try {
      setIsLoading(true)
      const script = await generateScript(outline, questions)
      setLocalScript(script)
      toast({
        title: "生成成功",
        description: "已成功生成播客文字稿",
        status: "success",
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      console.error('Error generating script:', error)
      toast({
        title: "生成失败",
        description: "生成播客文字稿时出现错误，请稍后重试",
        status: "error",
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Box minH="100vh" bg="gray.50">
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
              onClick={handleGenerateScript}
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
              onChange={(e) => setLocalScript(e.target.value)}
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