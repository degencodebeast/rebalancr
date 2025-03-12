'use client'

import { useRef, useState, useEffect } from 'react'
import DashboardLayout from '@/components/Layout/DashboardLayout'
import { usePrivy } from '@privy-io/react-auth'
import { Textarea, Paper, ScrollArea, Avatar } from '@mantine/core'
import SendIcon from '@/components/icons/SendIcon'
import '@/app/dashboard/chats.scss'
import { Button } from '@/components/ui/button'
import { blo } from 'blo'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import LogoImg from '../../../public/rebalancr_black.webp'
import Image from 'next/image'
import { useWebSocketWithAuth } from '@/hooks/useWebSocketWithAuth'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { selectHasVerified } from '@/store/auth/authSlice'

// Message type definition
interface Message {
  id: string
  sender: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function Dashboard() {
  const { user } = usePrivy()
  const [inputMessage, setInputMessage] = useState('')
  const viewportRef = useRef<HTMLDivElement>(null)
  const welcomeMessageShownRef = useRef(false)
  const router = useRouter()
  const hasVerified = useSelector(selectHasVerified)
  
  // Use our custom hook for WebSocket communication
  const { 
    isConnected, 
    isAuthenticated, 
    isAuthenticating, 
    error, 
    messages, 
    sendMessage 
  } = useWebSocketWithAuth()
  
  // Add welcome message
  useEffect(() => {
    if (!welcomeMessageShownRef.current && isAuthenticated && messages.length === 0) {
      setTimeout(() => {
        const welcomeMessage = {
          id: `welcome-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
          sender: 'assistant' as const,
          content: 'Hi Anon, you are about to start chatting with rebalancr. An AI automated portfolio management system predicting optimal assets allocation to ensure maximum profits and to cut loses.',
          timestamp: new Date(),
        };
        // The addLocalMessage functionality is now handled within the hook's sendMessage
        welcomeMessageShownRef.current = true;
      }, 1000);
    }
  }, [isAuthenticated, messages.length]);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (viewportRef.current) {
      viewportRef.current.scrollTo({
        top: viewportRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  // Redirect to home if not verified
  useEffect(() => {
    if (!hasVerified) {
      router.push('/')
    }
  }, [hasVerified, router])
  
  // Show loading until verification is confirmed
  if (!hasVerified) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin h-10 w-10 border-t-2 border-b-2 border-[#8c52ff] rounded-full mx-auto mb-4"></div>
          <p className="text-lg">Verifying authentication...</p>
        </div>
      </div>
    )
  }

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !isConnected || !isAuthenticated) return;
    
    // Send message using our hook
    sendMessage(inputMessage);
    
    // Clear input
    setInputMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Show authentication status
  const getStatusMessage = () => {
    if (error) return `Error: ${error}`;
    if (isAuthenticating) return 'Authenticating...';
    if (!isConnected) return 'Connecting...';
    if (!isAuthenticated) return 'Waiting for authentication...';
    return 'Connected';
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-80px)] py-4 md:px-4">
        {/* Connection status indicator */}
        {(!isConnected || !isAuthenticated || isAuthenticating || error) && (
          <div className={`mb-4 p-2 text-center rounded-md ${error ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
            {getStatusMessage()}
          </div>
        )}
        
        {/* Chat messages area */}
        <ScrollArea
          className="flex-grow px-2 py-4 md:px-4 chat-container bg-white md:rounded-lg shadow-sm border border-[#f1f1f1]"
          viewportRef={viewportRef}
        >
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-row ${
                message.sender === 'user' ? 'user-message' : 'assistant-message'
              }`}
            >
              <div className="avatar-container hidden md:block">
                {message.sender === 'assistant' ? (
                  <Image
                    src={LogoImg}
                    className="w-7 h-6 md:w-10 md:h-8"
                    alt="Rebalancer Logo"
                  />
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
        <div className="pt-4 px-2 md:px-0">
          <Textarea
            className="flex-grow chat-input"
            placeholder={isAuthenticated ? "Type your prompt here..." : "Waiting for connection..."}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            autosize
            maxRows={8}
            minRows={1}
            disabled={!isAuthenticated}
            rightSection={
              <Button
                onClick={handleSendMessage}
                disabled={!isAuthenticated || !inputMessage.trim()}
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
  );
}
