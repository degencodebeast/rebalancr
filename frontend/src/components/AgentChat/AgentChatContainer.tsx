import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { v4 as uuidv4 } from 'uuid';
import { Card, CardHeader, CardContent, CardFooter } from '../../components/ui/card';

import ChatHistory from './ChatHistory';
import ChatInput from './ChatInput';
import { AppDispatch, RootState } from '../../store';
import { connectWebSocket, sendWebSocketMessage } from '../../store/chat/webSocketSlice';

interface AgentChatContainerProps {
  userId: string;
}

const AgentChatContainer: React.FC<AgentChatContainerProps> = ({ userId }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { connected, messages: wsMessages, isLoading } = useSelector(
    (state: RootState) => state.webSocket
  );
  
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  
  // Connect to WebSocket when component mounts
  useEffect(() => {
    dispatch(connectWebSocket(userId));
    
    return () => {
      // Cleanup WebSocket connection when component unmounts
      const socket = (window as any).chatSocket;
      if (socket) {
        socket.close();
      }
    };
  }, [dispatch, userId]);
  
  // Process incoming WebSocket messages
  useEffect(() => {
    if (wsMessages.length > 0) {
      const latestMessage = wsMessages[wsMessages.length - 1];
      
      if (latestMessage.type === 'agent_message' || latestMessage.type === 'tool_execution') {
        setChatMessages(prev => [
          ...prev,
          {
            id: latestMessage.message_id || uuidv4(),
            content: latestMessage.content,
            sender: 'agent',
            timestamp: Date.now(),
            type: latestMessage.type
          }
        ]);
      }
    }
  }, [wsMessages]);
  
  const handleSendMessage = (message: string) => {
    // Add user message to chat
    const userMessage = {
      id: uuidv4(),
      content: message,
      sender: 'user' as const,
      timestamp: Date.now()
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    
    // Send message via WebSocket
    dispatch(sendWebSocketMessage(message));
  };
  
  return (
    <Card className="h-full flex flex-col border-2 shadow-md">
      <CardHeader className="pb-2 pt-4 px-4 bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-lg">Rebalancr Portfolio Agent</h3>
          <div className="text-xs flex items-center rounded-full bg-white/10 px-2 py-1">
            <span className={`inline-block h-2 w-2 rounded-full mr-2 ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
            {connected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-0 flex-grow overflow-hidden">
        <ChatHistory 
          messages={chatMessages}
          isLoading={isLoading}
        />
      </CardContent>
      
      <CardFooter className="p-0">
        <ChatInput 
          onSendMessage={handleSendMessage}
          disabled={!connected}
          isLoading={isLoading}
        />
      </CardFooter>
    </Card>
  );
};

export default AgentChatContainer; 