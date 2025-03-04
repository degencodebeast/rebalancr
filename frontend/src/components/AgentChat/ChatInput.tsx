import React, { useState } from 'react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { SendIcon } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  isLoading = false,
  disabled = false
}) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  return (
    <form 
      onSubmit={handleSubmit}
      className="p-4 border-t border-gray-200 bg-white w-full"
    >
      <div className="flex items-center gap-2">
        <Input
          className="flex-1 shadow-sm focus-visible:ring-blue-500 rounded-full px-4 h-12"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={disabled}
          autoComplete="off"
        />
        <Button 
          type="submit"
          className="rounded-full bg-blue-600 hover:bg-blue-700 h-12 w-12 flex-shrink-0"
          disabled={!message.trim() || isLoading}
        >
          {isLoading ? (
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-current border-t-transparent" />
          ) : (
            <SendIcon className="h-5 w-5" />
          )}
        </Button>
      </div>
    </form>
  );
};

export default ChatInput; 