'use client';
import { useState, useEffect } from 'react';

export default function WebSocketTest() {
  const [messages, setMessages] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      setConnected(true);
      // Test message
      ws.send(JSON.stringify({type: 'get_portfolio'}));
    };
    
    ws.onmessage = (event) => {
      const newMessage = JSON.parse(event.data);
      setMessages(prev => [...prev, newMessage]);
    };
    
    ws.onclose = () => setConnected(false);
    
    return () => ws.close();
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">WebSocket Test</h1>
      <p className="mb-4">
        Status: <span className={connected ? "text-green-500" : "text-red-500"}>
          {connected ? "✅ Connected" : "❌ Disconnected"}
        </span>
      </p>
      <div className="border p-4 rounded-md bg-gray-50">
        <h2 className="text-xl font-semibold mb-2">Messages:</h2>
        <pre className="whitespace-pre-wrap overflow-auto max-h-96">
          {JSON.stringify(messages, null, 2)}
        </pre>
      </div>
    </div>
  );
} 