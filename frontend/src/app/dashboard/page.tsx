'use client'

import { useState, useEffect, useRef } from 'react'
import DashboardLayout from '@/components/Layout/DashboardLayout'
import { usePrivy } from '@privy-io/react-auth'
import { Textarea, Paper, ScrollArea, Avatar, Text } from '@mantine/core'
import SendIcon from '@/components/icons/SendIcon'
import '@/app/dashboard/chats.scss'
import { Button } from '@/components/ui/button'
import { blo } from 'blo'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// Message type definition
interface Message {
  id: string
  sender: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function Dashboard() {
  const { user } = usePrivy()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [wsConnected, setWsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const viewportRef = useRef<HTMLDivElement>(null)
  const welcomeMessageShownRef = useRef(false)

  // Connect to WebSocket
  useEffect(() => {
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL || '')
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected')
      setWsConnected(true)

      // Send initial message to get any existing data
      ws.send(JSON.stringify({ type: 'get_portfolio' }))
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('Received message:', data)

      // Handle different message types
      if (data.type === 'chat_message') {
        addMessage({
          id: `assistant-${Date.now()}-${Math.random()
            .toString(36)
            .substring(2, 9)}`,
          sender: 'assistant',
          content: data.content,
          timestamp: new Date(),
        })
      }
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setWsConnected(false)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [])

  // Create a separate useEffect for the welcome message
  // useEffect(() => {
  //   //Add welcome message only once
  //   if (!welcomeMessageShownRef.current && messages.length === 0) {
  //     setTimeout(() => {
  //       addMessage({
  //         id: `welcome-${Date.now()}-${Math.random()
  //           .toString(36)
  //           .substring(2, 9)}`,
  //         sender: 'assistant',
  //         content:
  //           'Hi Anon, you are about to start chatting with rebalancr. An AI automated portfolio management system predicting optimal assets allocation to ensure maximum profits and to cut loses.',
  //         timestamp: new Date(),
  //       })
  //       welcomeMessageShownRef.current = true
  //     }, 1000)
  //   }
  // }, [])

  useEffect(() => {
    if (!welcomeMessageShownRef.current) {
      setTimeout(() => {
        setMessages((prev) => {
          if (prev.length === 0) {
            welcomeMessageShownRef.current = true
            return [
              ...prev,
              {
                id: `welcome-${Date.now()}-${Math.random()
                  .toString(36)
                  .substring(2, 9)}`,
                sender: 'assistant',
                content:
                  'Hi Anon, you are about to start chatting with rebalancr. An AI automated portfolio management system predicting optimal assets allocation to ensure maximum profits and to cut loses.',
                timestamp: new Date(),
              },
            ]
          }
          return prev
        })
      }, 1000)
    }
  }, [])

  // Scroll to bottom when messages change
  useEffect(() => {
    if (viewportRef.current) {
      viewportRef.current.scrollTo({
        top: viewportRef.current.scrollHeight,
        behavior: 'smooth',
      })
    }
  }, [messages])

  const addMessage = (message: Message) => {
    setMessages((prev) => [...prev, message])
  }

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return

    // Add user message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: inputMessage,
      timestamp: new Date(),
    }
    addMessage(userMessage)

    // Send message to server
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'chat_message',
          content: inputMessage,
          userId: user?.wallet?.address,
        }),
      )
    }

    setInputMessage('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-80px)] bg-[#3f3f3f]">
        {/* Chat messages area */}
        <ScrollArea
          className="flex-grow px-2 py-4 md:px-4 chat-container"
          viewportRef={viewportRef}
        >
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-row ${
                message.sender === 'user' ? 'user-message' : 'assistant-message'
              }`}
            >
              <div className="avatar-container">
                {message.sender === 'assistant' ? (
                  <Avatar size={32} color="white" radius="xl" bg="#121212">
                    AI
                  </Avatar>
                ) : (
                  <Avatar
                    size={32}
                    radius="xl"
                    bg="#8c52ff"
                    color="white"
                    src={blo(`0x${user?.wallet?.address}`)}
                  >
                    {user?.wallet?.address?.substring(0, 2) || 'U'}
                  </Avatar>
                )}
              </div>

              <Paper
                p="md"
                withBorder
                className={`message-bubble ${
                  message.sender === 'user' ? 'user-bubble' : 'assistant-bubble'
                }`}
                style={{
                  boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                }}
              >
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                </div>
              </Paper>
            </div>
          ))}
        </ScrollArea>

        {/* Input area */}
        <div className="px-4 pb-6">
          <Textarea
            className="flex-grow chat-input"
            placeholder="Type your prompt here..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            autosize
            maxRows={8}
            minRows={1}
            rightSection={
              <Button
                onClick={handleSendMessage}
                disabled={!wsConnected || !inputMessage.trim()}
                variant="default"
                className="flex items-center gap-2"
              >
                <span>Send</span>
                <SendIcon />
              </Button>
            }
          />
        </div>
      </div>
    </DashboardLayout>
  )
}
