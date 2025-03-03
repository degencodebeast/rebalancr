'use client'

import { useState, useEffect, useRef } from 'react'
import DashboardLayout from '@/components/Layout/DashboardLayout'
import { usePrivy } from '@privy-io/react-auth'
import {
  Button,
  TextInput,
  Paper,
  ScrollArea,
  Avatar,
  Text,
  Group,
} from '@mantine/core'
import SendIcon from '@/components/icons/SendIcon'

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
          id: Date.now().toString(),
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

    // Add welcome message
    setTimeout(() => {
      addMessage({
        id: 'welcome',
        sender: 'assistant',
        content:
          'Welcome to Rebalancr! How can I help you with your portfolio today?',
        timestamp: new Date(),
      })
    }, 1000)

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
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
      <div className="flex flex-col h-[calc(100vh-80px)]">
        <div className="p-4 border-b">
          <h1 className="text-2xl font-bold">Chat with Rebalancr</h1>
          <div className="flex items-center mt-2">
            <div
              className={`w-3 h-3 rounded-full mr-2 ${
                wsConnected ? 'bg-green-500' : 'bg-red-500'
              }`}
            ></div>
            <span className="text-sm text-gray-600">
              {wsConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        {/* Chat messages area */}
        <ScrollArea className="flex-grow p-4" viewportRef={viewportRef}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`mb-4 flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <Paper
                p="md"
                withBorder
                className={`max-w-[80%] ${
                  message.sender === 'user'
                    ? 'bg-blue-50 border-blue-200'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <Group align="flex-start" mb={5}>
                  {message.sender === 'assistant' && (
                    <Avatar color="blue" radius="xl">
                      AI
                    </Avatar>
                  )}
                  <div>
                    <Text size="sm" c="dimmed">
                      {message.sender === 'user'
                        ? 'You'
                        : 'Rebalancr Assistant'}
                    </Text>
                    <Text>{message.content}</Text>
                  </div>
                  {message.sender === 'user' && (
                    <Avatar color="indigo" radius="xl">
                      {user?.wallet?.address?.substring(0, 2) || 'U'}
                    </Avatar>
                  )}
                </Group>
              </Paper>
            </div>
          ))}
        </ScrollArea>

        {/* Input area */}
        <div className="p-4 border-t">
          <div className="flex">
            <TextInput
              className="flex-grow"
              placeholder="Type your message here..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              rightSection={
                <Button
                  onClick={handleSendMessage}
                  disabled={!wsConnected || !inputMessage.trim()}
                  variant="subtle"
                  color="blue"
                >
                  <SendIcon />
                </Button>
              }
            />
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
