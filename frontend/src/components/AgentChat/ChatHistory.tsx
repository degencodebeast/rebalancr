import React, { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: number;
  type?: string;
}

interface ChatHistoryProps {
  messages: Message[];
  isLoading?: boolean;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-grow overflow-auto p-4 flex flex-col gap-2">
      {messages.length === 0 && !isLoading ? (
        <div className="flex justify-center items-center h-full opacity-70">
          <p className="text-muted-foreground">
            Start a conversation with your portfolio agent!
          </p>
        </div>
      ) : (
        messages.map((message) => (
          <ChatMessage
            key={message.id}
            content={message.content}
            sender={message.sender}
            timestamp={message.timestamp}
            connected={true}
            type={message.type}
          />
        ))
      )}
      
      {isLoading && (
        <div className="flex justify-center p-2">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatHistory; 