'use client'

import { useState } from 'react'
import { usePodcastContext } from '../context/PodcastContext'
import { getDailyNews } from '../utils/api'
import {
  Button,
  Textarea,
  Box,
  useToast,
  Spinner,
  Text
} from '@chakra-ui/react'
import Link from 'next/link'

export default function ContentAcquisition() {
  const { setContent } = usePodcastContext()
  const [isLoading, setIsLoading] = useState(false)
  const [content, setLocalContent] = useState('')
  const [error, setError] = useState('')
  const toast = useToast()

  const handleGetDailyNews = async () => {
    try {
      setIsLoading(true)
      setError('')
      const news = await getDailyNews()
      setLocalContent(news)
      setContent(news)
      toast({
        title: '获取成功',
        description: '已成功获取今日早报',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      console.error('Error fetching daily news:', error)
      const errorMessage = error instanceof Error ? error.message : '获取新闻失败，请稍后重试'
      setError(errorMessage)
      toast({
        title: '获取失败',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value
    setLocalContent(newContent)
    setContent(newContent)
  }

  return (
    <Box maxW="6xl" mx="auto" py={8} px={4}>
      <Box mb={6}>
        <Button
          onClick={handleGetDailyNews}
          isDisabled={isLoading}
          colorScheme="green"
          size="lg"
          leftIcon={isLoading ? <Spinner size="sm" /> : undefined}
        >
          {isLoading ? '获取中...' : '获取今日早报'}
        </Button>
      </Box>

      {error && (
        <Box mb={6} p={4} bg="red.50" color="red.500" rounded="md">
          <Text>{error}</Text>
        </Box>
      )}

      <Box bg="white" rounded="xl" shadow="lg" p={6} mb={6}>
        <Textarea
          value={content}
          onChange={handleContentChange}
          placeholder="在此输入或粘贴内容..."
          minH="500px"
          p={6}
          fontSize="lg"
          isDisabled={isLoading}
        />
      </Box>

      <Box display="flex" justifyContent="flex-end">
        <Button
          as={Link}
          href="/content-outline"
          colorScheme="blue"
          size="lg"
          isDisabled={!content.trim()}
        >
          下一步
        </Button>
      </Box>
    </Box>
  )
}

