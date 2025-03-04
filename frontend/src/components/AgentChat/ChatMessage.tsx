import React from 'react';
import { cn } from '../../lib/utils';

interface ChatMessageProps {
  content: string;
  sender: 'user' | 'agent';
  timestamp: number;
  type?: string;
  connected: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ content, sender, timestamp, type, connected }) => {
  const formattedTime = new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });

  return (
    <div className={cn(
      "flex items-end mb-4 w-full",
      sender === 'user' ? "justify-end" : "justify-start"
    )}>
      {sender === 'agent' && (
        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gradient-to-r from-blue-600 to-indigo-700 flex items-center justify-center text-white mr-2">
          A
        </div>
      )}
      
      <div className="max-w-[70%]">
        <div className={cn(
          "px-4 py-2 rounded-xl shadow-sm",
          sender === 'user' 
            ? "bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-br-none" 
            : "bg-gray-100 text-gray-800 rounded-bl-none border border-gray-200",
          type === 'tool_execution' && "bg-amber-50 text-amber-800 italic border border-amber-200"
        )}>
          {type === 'tool_execution' ? (
            <p className="text-sm"><em>Working: {content}</em></p>
          ) : (
            <p>{content}</p>
          )}
        </div>
        <span className={cn(
          "text-xs text-gray-500 block mt-1",
          sender === 'user' ? "text-right" : "text-left"
        )}>
          {formattedTime}
        </span>
        <span className={`inline-block h-2 w-2 rounded-full mr-2 ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
        {connected ? 'Connected' : 'Disconnected'}
      </div>

      {sender === 'user' && (
        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gradient-to-r from-blue-600 to-indigo-700 flex items-center justify-center text-white ml-2">
          Y
        </div>
      )}
    </div>
  );
};

export default ChatMessage; 