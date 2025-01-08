'use client'

import { useState } from 'react'
import { usePodcastContext } from '../context/PodcastContext'
import { generateScript } from '../utils/api'
import { Button, useToast, Alert, AlertIcon, Textarea } from '@chakra-ui/react'
import Link from 'next/link'

export default function PodcastGeneration() {
  const { outline, questions, setGeneratedScript } = usePodcastContext()
  const [isLoading, setIsLoading] = useState(false)
  const [localScript, setLocalScript] = useState('')
  const toast = useToast()

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
      const result = await generateScript(outline, questions)
      
      // 转换文本格式：将 **Andy:** 和 **Amily:** 转换为正确的格式
      const formattedResult = result
        .replace(/\*\*Andy:\*\* /g, 'Andy："')
        .replace(/\*\*Amily:\*\* /g, 'Amily："')
        .split('\n')
        .map((line: string) => {
          if (line.startsWith('Andy："') || line.startsWith('Amily："')) {
            return line + '"'  // 为每行对话添加结束引号
          }
          return line
        })
        .join('\n')
      
      setLocalScript(formattedResult)
      setGeneratedScript(formattedResult)
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
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">播客文字稿生成</h1>
      </div>

      {(!outline || !questions) && (
        <div className="mb-6">
          <Alert status="warning">
            <AlertIcon />
            请先在上一页生成大纲和问题
          </Alert>
        </div>
      )}

      <div className="mb-6">
        <Button
          onClick={handleGenerateScript}
          isLoading={isLoading}
          loadingText="生成中..."
          colorScheme="green"
          size="lg"
          isDisabled={!outline || !questions}
        >
          生成播客文字稿
        </Button>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <Textarea
          value={localScript}
          onChange={(e) => {
            setLocalScript(e.target.value)
            setGeneratedScript(e.target.value)
          }}
          placeholder={'点击"生成播客文字稿"按钮，生成对话内容...'}
          minH="500px"
          fontSize="lg"
          isDisabled={!outline || !questions}
        />
      </div>

      <div className="flex justify-between">
        <Link href="/content-outline">
          <Button colorScheme="gray" size="lg">
            上一步
          </Button>
        </Link>
        <Link href="/audio-generation">
          <Button
            colorScheme="blue"
            size="lg"
            isDisabled={!localScript.trim()}
          >
            下一步
          </Button>
        </Link>
      </div>
    </div>
  )
} 