'use client'

import React, { createContext, useContext, useState } from 'react'

interface PodcastContextType {
  content: string
  setContent: (content: string) => void
  outline: string
  setOutline: (outline: string) => void
  questions: string
  setQuestions: (questions: string) => void
  script: string
  setScript: (script: string) => void
  generatedScript: string
  setGeneratedScript: (script: string) => void
}

const PodcastContext = createContext<PodcastContextType | undefined>(undefined)

export function PodcastProvider({ children }: { children: React.ReactNode }) {
  const [content, setContent] = useState('')
  const [outline, setOutline] = useState('')
  const [questions, setQuestions] = useState('')
  const [script, setScript] = useState('')
  const [generatedScript, setGeneratedScript] = useState('')

  return (
    <PodcastContext.Provider
      value={{
        content,
        setContent,
        outline,
        setOutline,
        questions,
        setQuestions,
        script,
        setScript,
        generatedScript,
        setGeneratedScript
      }}
    >
      {children}
    </PodcastContext.Provider>
  )
}

export function usePodcastContext() {
  const context = useContext(PodcastContext)
  if (context === undefined) {
    throw new Error('usePodcastContext must be used within a PodcastProvider')
  }
  return context
}

