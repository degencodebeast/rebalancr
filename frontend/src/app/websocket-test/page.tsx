'use client';
import { useState, useEffect } from 'react';

export default function WebSocketTest() {
  const [messages, setMessages] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      console.log('Connection established');
      setConnected(true);
      setSocket(ws);
      // Don't send here - will send after connection confirmed
    };
    
    ws.onmessage = (event) => {
      const newMessage = JSON.parse(event.data);
      setMessages(prev => [...prev, newMessage]);
    };
    
    ws.onclose = () => {
      console.log('Connection closed');
      setConnected(false);
      setSocket(null);
    };
    
    return () => ws.close();
  }, []);

  // Function to send message only when connected
  const sendTestMessage = () => {
    if (socket && connected) {
      console.log('Sending test message');
      socket.send(JSON.stringify({type: 'get_portfolio'}));
    } else {
      console.warn('Cannot send: WebSocket not connected');
    }
  };

  // Send test message once connected
  useEffect(() => {
    if (connected && socket) {
      // Wait a short moment to be sure
      const timer = setTimeout(() => {
        sendTestMessage();
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [connected]);

  return (
    <div className="p-4 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-4 text-gray-900">WebSocket Test</h1>
      <p className="mb-4 text-gray-800">
        Status: <span className={connected ? "text-green-600 font-semibold" : "text-red-600 font-semibold"}>
          {connected ? "✅ Connected" : "❌ Disconnected"}
        </span>
      </p>
      <button 
        onClick={sendTestMessage}
        className="px-4 py-2 bg-blue-600 text-white rounded mb-4 hover:bg-blue-700 transition-colors"
        disabled={!connected}
      >
        Send Test Message
      </button>
      <div className="border border-gray-300 p-4 rounded-md bg-white shadow-sm">
        <h2 className="text-xl font-semibold mb-2 text-gray-800">Messages:</h2>
        <pre className="whitespace-pre-wrap overflow-auto max-h-96 p-3 bg-gray-50 border border-gray-200 rounded text-gray-800 text-sm">
          {JSON.stringify(messages, null, 2)}
        </pre>
      </div>
    </div>
  );
} 