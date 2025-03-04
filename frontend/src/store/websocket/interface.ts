export interface Message {
  id: string
  sender: 'user' | 'assistant'
  content: string
  timestamp: Date
}
