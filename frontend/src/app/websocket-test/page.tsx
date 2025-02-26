'use client'
import { Button } from '@/components/ui/button'
import { useGetWebSocketMessagesQuery } from '@/store/websocket/websocketApi'

export default function WebSocketTest() {
  const { data: messages = [], isSuccess: connected } =
    useGetWebSocketMessagesQuery()

  const handleSendTestMessage = () => {
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL || '')
    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'test_message' }))
      ws.close() // Clean up after sending
    }
  }

  return (
    <div className="p-4 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-4 text-gray-900">WebSocket Test</h1>
      <p className="mb-4 text-gray-800">
        Status:{' '}
        <span
          className={
            connected
              ? 'text-green-600 font-semibold'
              : 'text-red-600 font-semibold'
          }
        >
          {connected ? '✅ Connected' : '❌ Disconnected'}
        </span>
      </p>
      <Button className="mb-6" onClick={handleSendTestMessage}>
        Send Test Message
      </Button>
      <div className="border border-gray-300 p-4 rounded-md bg-white shadow-sm">
        <h2 className="text-xl font-semibold mb-2 text-gray-800">Messages:</h2>
        <pre className="whitespace-pre-wrap overflow-auto max-h-96 p-3 bg-gray-50 border border-gray-200 rounded text-gray-800 text-sm">
          {JSON.stringify(messages, null, 2)}
        </pre>
      </div>
    </div>
  )
}
