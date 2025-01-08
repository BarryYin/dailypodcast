'use client'

import { useState, useEffect } from 'react'
import { usePodcastContext } from '../context/PodcastContext'
import {
  Grid,
  Box,
  Button,
  Textarea,
  Heading,
  VStack,
  useToast,
  Text,
  Alert,
  AlertIcon,
} from '@chakra-ui/react'
import Link from 'next/link'
import { generateOutline, generateQuestions, updateNewsCache } from '../utils/api'
import { useRouter } from 'next/navigation'

export default function ContentOutline() {
  const router = useRouter()
  const { content, setOutline, setQuestions } = usePodcastContext()
  const [isLoading, setIsLoading] = useState({ outline: false, questions: false })
  const [outline, setLocalOutline] = useState('')
  const [localQuestions, setLocalQuestions] = useState('')
  const toast = useToast()

  useEffect(() => {
    // 如果没有内容，提示用户返回上一页
    if (!content) {
      toast({
        title: "未找到内容",
        description: "请先在上一页输入或获取早报内容",
        status: "warning",
        duration: 5000,
        isClosable: true,
      })
    }
  }, [content, toast])

  const handleGenerateOutline = async () => {
    if (!content) {
      toast({
        title: "无法生成",
        description: "请先返回上一页输入或获取早报内容",
        status: "error",
        duration: 3000,
        isClosable: true,
      })
      return
    }

    try {
      setIsLoading(prev => ({ ...prev, outline: true }))
      const result = await generateOutline(content)
      setLocalOutline(result)
      setOutline(result)
      // 保存大纲到缓存
      await updateNewsCache({ outline: result })
      toast({
        title: "生成成功",
        description: "已成功生成内容大纲",
        status: "success",
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      console.error('Error generating outline:', error)
      toast({
        title: "生成失败",
        description: "生成大纲时出现错误，请稍后重试",
        status: "error",
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsLoading(prev => ({ ...prev, outline: false }))
    }
  }

  const handleGenerateQuestions = async () => {
    if (!content) {
      toast({
        title: "无法生成",
        description: "请先返回上一页输入或获取早报内容",
        status: "error",
        duration: 3000,
        isClosable: true,
      })
      return
    }

    try {
      setIsLoading(prev => ({ ...prev, questions: true }))
      const result = await generateQuestions(content)
      setLocalQuestions(result)
      setQuestions(result)
      // 保存问题到缓存
      await updateNewsCache({ questions: result })
      toast({
        title: "生成成功",
        description: "已成功生成相关问题",
        status: "success",
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      console.error('Error generating questions:', error)
      toast({
        title: "生成失败",
        description: "生成问题时出现错误，请稍后重试",
        status: "error",
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsLoading(prev => ({ ...prev, questions: false }))
    }
  }

  // 手动修改内容时也保存到缓存
  const handleOutlineChange = async (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newOutline = e.target.value
    setLocalOutline(newOutline)
    setOutline(newOutline)
    await updateNewsCache({ outline: newOutline })
  }

  const handleQuestionsChange = async (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newQuestions = e.target.value
    setLocalQuestions(newQuestions)
    setQuestions(newQuestions)
    await updateNewsCache({ questions: newQuestions })
  }

  return (
    <Box maxW="8xl" mx="auto" py={8} px={4}>
      {!content && (
        <Alert status="warning" mb={6}>
          <AlertIcon />
          未检测到早报内容，请先返回上一页输入或获取早报内容
        </Alert>
      )}
      <Grid templateColumns={{ base: "1fr", md: "1fr 1fr" }} gap={6}>
        {/* 左侧：大纲部分 */}
        <Box>
          <VStack align="stretch" spacing={4}>
            <Heading size="lg" mb={4}>内容大纲</Heading>
            <Button
              onClick={handleGenerateOutline}
              isLoading={isLoading.outline}
              loadingText="生成中..."
              colorScheme="green"
              size="lg"
              mb={4}
              isDisabled={!content}
            >
              生成大纲
            </Button>
            <Box bg="white" rounded="xl" shadow="lg" p={6}>
              <Textarea
                value={outline}
                onChange={handleOutlineChange}
                placeholder={content ? '点击"生成大纲"按钮，或在此输入大纲内容...' : '请先返回上一页输入早报内容...'}
                minH="500px"
                p={4}
                fontSize="lg"
                isDisabled={!content}
              />
            </Box>
          </VStack>
        </Box>

        {/* 右侧：问题部分 */}
        <Box>
          <VStack align="stretch" spacing={4}>
            <Heading size="lg" mb={4}>相关问题</Heading>
            <Button
              onClick={handleGenerateQuestions}
              isLoading={isLoading.questions}
              loadingText="生成中..."
              colorScheme="blue"
              size="lg"
              mb={4}
              isDisabled={!content}
            >
              生成问题
            </Button>
            <Box bg="white" rounded="xl" shadow="lg" p={6}>
              <Textarea
                value={localQuestions}
                onChange={handleQuestionsChange}
                placeholder='点击"生成问题"按钮，或在此输入问题内容...'
                minH="500px"
                p={4}
                fontSize="lg"
                isDisabled={!content}
              />
            </Box>
          </VStack>
        </Box>
      </Grid>

      {/* 底部导航 */}
      <Box display="flex" justifyContent="space-between" mt={8}>
        <Link href="/content-acquisition" passHref>
          <Button as="a" colorScheme="gray" size="lg">
            上一步
          </Button>
        </Link>
        <Link href="/podcast-generation" passHref>
          <Button
            as="a"
            colorScheme="blue"
            size="lg"
            isDisabled={!outline.trim() || !localQuestions.trim()}
          >
            下一步
          </Button>
        </Link>
      </Box>
    </Box>
  )
}

