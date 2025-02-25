# Rebalancr Frontend

AI-powered portfolio rebalancing for DeFi investors. This frontend application provides an intuitive interface for portfolio management, AI-assisted trading, and yield optimization.

## Setup

1. Install dependencies:
   ```bash
   pnpm install
   ```

2. Run the development server:
   ```bash
   pnpm dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Features

- Portfolio visualization and management
- AI-powered trading recommendations
- Real-time market updates via WebSockets
- DeFi yield optimization

## Development

- Built with Next.js 14 using the App Router
- TypeScript for type safety
- Tailwind CSS for styling
- WebSocket integration for real-time data

## Project Structure

The project follows a feature-based organization:

- `src/app/*` - Next.js pages using App Router
- `src/components/*` - Reusable React components
- `src/hooks/*` - Custom React hooks
- `src/lib/*` - Utility functions and services

## Testing WebSocket Connection

### Frontend Testing
Visit the `/websocket-test` page to test WebSocket connectivity with the backend server. This page provides:
- Connection status indicator
- Automatic test message on connection
- Message log display

### Alternative Testing Methods

#### Browser Console
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (event) => console.log('Received:', JSON.parse(event.data));
ws.send(JSON.stringify({type: 'get_portfolio'}));
```

#### Command Line (wscat)
```bash
# Install wscat
npm install -g wscat

# Connect and test
wscat -c ws://localhost:8000/ws
> {"type":"get_portfolio"}
```

Make sure your FastAPI backend server is running before testing WebSocket connections.
