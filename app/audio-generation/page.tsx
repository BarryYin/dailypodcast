'use client'

import { useState, useEffect } from 'react'
import { usePodcastContext } from '../context/PodcastContext'
import { generateAudio } from '../utils/api'
import { Button, useToast, Textarea, Box } from '@chakra-ui/react'
import Link from 'next/link'

export default function AudioGeneration() {
  const { script, setScript, generatedScript } = usePodcastContext()
  const [isLoading, setIsLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState('')
  const toast = useToast()

  // 当组件加载时，如果有生成的文字稿，就使用它
  useEffect(() => {
    if (generatedScript && !script) {
      setScript(generatedScript)
    }
  }, [generatedScript, script, setScript])

  const handleGenerateAudio = async () => {
    if (!script.trim()) {
      toast({
        title: "无法生成",
        description: "请确保有文字稿内容",
        status: "error",
        duration: 3000,
        isClosable: true,
      })
      return
    }

    try {
      setIsLoading(true)
      const filename = await generateAudio(script)
      
      if (!filename) {
        throw new Error('未能获取音频文件名')
      }
      
      // 构建完整的音频文件 URL，使用绝对路径
      const fullUrl = `http://localhost:8000/audio/${filename}`
      console.log('Audio URL:', fullUrl)  // 添加日志
      setAudioUrl(fullUrl)
      
      toast({
        title: "生成成功",
        description: "已成功生成音频文件",
        status: "success",
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      console.error('Error generating audio:', error)
      toast({
        title: "生成失败",
        description: error instanceof Error ? error.message : "生成音频时出现错误，请稍后重试",
        status: "error",
        duration: 5000,
        isClosable: true,
      })
      setAudioUrl('')  // 清除音频 URL
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Box maxW="6xl" mx="auto" py={8} px={4}>
      <Box mb={8}>
        <h1 className="text-3xl font-bold">音频生成</h1>
      </Box>

      <Box mb={6}>
        <Textarea
          value={script}
          onChange={(e) => setScript(e.target.value)}
          placeholder="在这里编辑或补充对话内容..."
          minH="300px"
          fontSize="lg"
        />
      </Box>

      <Box mb={6}>
        <Button
          onClick={handleGenerateAudio}
          isLoading={isLoading}
          loadingText="生成中..."
          colorScheme="green"
          size="lg"
          isDisabled={!script.trim()}
        >
          生成播客录音
        </Button>
      </Box>

      {audioUrl && (
        <Box mb={6}>
          <audio controls className="w-full" key={audioUrl}>
            <source src={audioUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        </Box>
      )}

      <Box display="flex" justifyContent="start">
        <Link href="/podcast-generation" passHref>
          <Button as="a" colorScheme="gray" size="lg">
            上一步
          </Button>
        </Link>
      </Box>
    </Box>
  )
}

