'use client';

import React from 'react';
import { usePrivy } from '@privy-io/react-auth';
import AgentChatContainer from '../../components/AgentChat/AgentChatContainer';

export default function AgentChatPage() {
  const { user, authenticated, ready } = usePrivy();

  // If Privy is still initializing, show loading state
  if (!ready) {
    return (
      <div className="container mx-auto pt-8">
        <div className="text-center py-8">
          <h2 className="text-xl font-medium">Loading authentication...</h2>
        </div>
      </div>
    );
  }

  // If user is not authenticated, show login message
  if (!authenticated) {
    return (
      <div className="container mx-auto pt-8">
        <div className="text-center py-8">
          <h2 className="text-xl font-medium">Please login to access the agent chat</h2>
        </div>
      </div>
    );
  }

  // User is authenticated, show chat interface
  return (
    <div className="container mx-auto pt-4 pb-8 h-[calc(100vh-120px)]">
      <h1 className="text-2xl font-bold mb-4">
        Chat with Your Portfolio Agent
      </h1>
      
      <div className="h-[calc(100vh-200px)] min-h-[500px]">
        <AgentChatContainer userId={user?.id || 'anonymous'} />
      </div>
    </div>
  );
} 